from django.db import transaction
import math
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import (
    SubAccount,
    PurchasedPhoneNumber,
    A2PRegistration,
    Contact,
    Tag,
    CalendarDetails,
    InspectionDetails,
    CustomUser,
)
from .serializers import (
    SubAccountSerializer,
    PhoneNumberSerializer,
    ContactSerializer,
    A2PRegistrationSerializer,
    CalendarDetailsSerializer,
    InspectionDetailsSerializer,
    CustomUserSerializer,
)
from drf_yasg.utils import swagger_auto_schema
import requests
from django.conf import settings
from .utils import (
    generate_dynamic_mapping,
    buy_phone_number_with_retries,
    a2pregister_with_retries,
    find_stripe_customer_id,
)

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from rest_framework.views import APIView
import stripe
import json


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.CALLBACK_URL
    client_class = OAuth2Client


class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]


class SubAccountViewSet(viewsets.ModelViewSet):
    queryset = SubAccount.objects.all()
    serializer_class = SubAccountSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new SubAccount and send data to GoHighLevel."
    )
    @action(detail=False, methods=["POST"])
    def create_subaccount(self, request):
        data = request.data
        data["user"] = request.user.pk
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            # First, save the data to your local database
            sub_account = serializer.save()

            # Construct the payload for GoHighLevel
            gohighlevel_payload = {
                "businessName": sub_account.business_name,
                "address": sub_account.address,
                "city": sub_account.city,
                "state": sub_account.state,
                "postalCode": sub_account.zip_code,
                "website": sub_account.website,
                "timezone": sub_account.timezone,
                "country": sub_account.country,
                "firstName": sub_account.first_name,
                "lastName": sub_account.last_name,
                "email": sub_account.business_email,
                "phone": sub_account.business_phone,
                "snapshot": {"id": "FzxccDUD3xd34OLELmnT", "type": "own"},
            }

            # Send data to GoHighLevel
            url = "https://rest.gohighlevel.com/v1/locations/"
            headers = {"Authorization": f"Bearer {settings.TOKEN}"}
            response = requests.post(url, headers=headers, json=gohighlevel_payload)
            if response.status_code == 200:
                response_data = response.json()
                sub_account.gohighlevel_id = response_data.get("id")
                sub_account.gohighlevel_api_key = response_data.get("apiKey")
                sub_account.save()  # Update the SubAccount instance with the new data
                user = request.user
                user.status = "Calendar Details"
                user.save()
                # Stripe Payment Details
                return Response(
                    {"message": "Subaccount created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Error creating subaccount in GoHighLevel"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CalendarDetailsViewSet(viewsets.ModelViewSet):
    queryset = CalendarDetails.objects.all()
    serializer_class = CalendarDetailsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the logged-in user and their associated SubAccount
        user = request.user
        sub_user = SubAccount.objects.get(user=user.pk)

        # Deserialize the incoming data
        data = request.data
        data["user"] = user.pk
        data["sub_account"] = sub_user.pk
        serializer = self.get_serializer(data=data)

        # Check if the deserialized data is valid
        if serializer.is_valid():
            # Save the CalendarDetails instance with user and sub_user fields set
            serializer.save()

            # Optionally, update the user status
            user.status = "Stripe Payment Details"
            user.save()

            return Response(
                {"message": "Calendar details created successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            # Return an error response if the data is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberViewSet(viewsets.ModelViewSet):
    queryset = PurchasedPhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Buy a new Phone NUmber from GoHighLevel."
    )
    @action(detail=False, methods=["POST"])
    def purchase_phone_number(self, request):
        # Retrieve the logged-in user's SubAccount
        user = request.user.pk
        sub_user = SubAccount.objects.get(user=user)

        if sub_user:
            phone = buy_phone_number_with_retries(
                sub_user.business_name, sub_user.business_phone
            )

            if phone:
                PurchasedPhoneNumber.objects.create(
                    phone_number=phone, sub_account=sub_user, user=request.user
                )
                user = request.user
                user.status = "A2P Registration"
                user.save()
                return Response(
                    {"message": "Phone Number purchased successfully"},
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "error": "Error purchasing number from GoHighLevel. Please try again."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"error": "Error purchasing number from GoHighLevel. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class A2PRegistrationViewSet(viewsets.ModelViewSet):
    queryset = A2PRegistration.objects.all()
    serializer_class = A2PRegistrationSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="A2PRegistration on  GoHighLevel.")
    @action(detail=False, methods=["POST"])
    def A2PRegistration(self, request):
        # Retrieve the logged-in user's SubAccount
        user = request.user.pk
        sub_user = SubAccount.objects.get(user=user)

        if sub_user:
            try:
                stats = a2pregister_with_retries(sub_user)

                if stats:
                    A2PRegistration.objects.create(
                        status="pending", sub_account=sub_user, user=request.user
                    )
                    user = request.user
                    user.status = "Contact Upload"
                    user.save()

                    return Response(
                        {"message": "A2PRegistration completed successfully"},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {
                            "error": "Error completing A2PRegistration on GoHighLevel. Please try again."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except:
                return Response(
                    {
                        "error": "Error completing A2PRegistration on GoHighLevel. Please try again."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "error": "Error completing A2PRegistration on GoHighLevel. Please try again."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Upload CSV, clean data, and send to GoHighLevel."
    )
    @action(detail=False, methods=["POST"])
    def upload_and_process(self, request):
        csv_file = request.FILES.get("csv_file")

        # Retrieve the logged-in user's SubAccount
        user = request.user.pk
        sub_user = SubAccount.objects.get(user=user)

        try:
            # Read CSV using pandas
            df = pd.read_csv(csv_file)

            # Cleaning logic
            # Remove people with the main company’s domain in their email address
            if "Primary Contact: website" in df.columns:
                for domain in df["Primary Contact: website"].dropna():
                    domain = domain.replace("www.", "")  # removing 'www.' if it's there
                    mask = ~df["Primary Contact: Email"].str.endswith(domain)
                    df = df[mask]

            # Drop empty columns and rows
            df.dropna(axis=1, how="all", inplace=True)
            df.dropna(axis=0, how="all", inplace=True)
            print("\nDropped any empty rows")

            # Get the column names from the CSV
            csv_columns = df.columns.tolist()

            # Get the Django model field names
            model_fields = [field.name for field in Contact._meta.fields]

            # Generate the dynamic mapping
            CSV_TO_MODEL_MAPPING = generate_dynamic_mapping(csv_columns, model_fields)
            print("\nGenerate dynamic mapping")

            # Determine the columns for names, emails, and phone based on the mapping
            first_name_column = next(
                (
                    csv_col
                    for csv_col, model_field in CSV_TO_MODEL_MAPPING.items()
                    if model_field == "first_name"
                ),
                None,
            )
            last_name_column = next(
                (
                    csv_col
                    for csv_col, model_field in CSV_TO_MODEL_MAPPING.items()
                    if model_field == "last_name"
                ),
                None,
            )
            email_column = next(
                (
                    csv_col
                    for csv_col, model_field in CSV_TO_MODEL_MAPPING.items()
                    if model_field == "email"
                ),
                None,
            )
            name_column = next(
                (
                    csv_col
                    for csv_col, model_field in CSV_TO_MODEL_MAPPING.items()
                    if model_field == "name"
                ),
                None,
            )
            phone_column = next(
                (
                    csv_col
                    for csv_col, model_field in CSV_TO_MODEL_MAPPING.items()
                    if model_field == "phone"
                ),
                None,
            )

            # Check if columns exist in the DataFrame and apply transformations
            if first_name_column in df.columns:
                df[first_name_column] = df[first_name_column].str.title()
                df = df[
                    ~df[first_name_column].str.contains("test", case=False, na=False)
                ]

            if last_name_column in df.columns:
                df[last_name_column] = df[last_name_column].str.title()
                df = df[
                    ~df[last_name_column].str.contains("test", case=False, na=False)
                ]

            # If there's no separate first and last name, but there's a combined name column
            if name_column in df.columns:
                df[name_column] = df[name_column].str.title()
                df = df[~df[name_column].str.contains("test", case=False, na=False)]

            # Remove any email that has the word 'test' in it
            if email_column in df.columns:
                df = df[~df[email_column].str.contains("test", case=False, na=False)]

            # Remove rows without both email and phone values
            if email_column in df.columns and phone_column in df.columns:
                df = df[df[email_column].notna() | df[phone_column].notna()]

            # Convert DataFrame back to a list of dictionaries for processing
            contacts_list = df.to_dict(orient="records")

            contacts_to_save = []

            print("\nsending contacts to Highlevel")
            for contact_data in contacts_list:
                # Filter out unwanted columns based on our mapping
                filtered_contact_data = {
                    CSV_TO_MODEL_MAPPING[key]: value
                    for key, value in contact_data.items()
                    if key in CSV_TO_MODEL_MAPPING
                }
                # Remove keys with nan values
                filtered_contact_data = {
                    k: v.strip() if isinstance(v, str) else v
                    for k, v in filtered_contact_data.items()
                    if not isinstance(v, float) or not math.isnan(v)
                }

                # Now, create a Contact instance using the filtered data
                contact = Contact(
                    **filtered_contact_data, sub_account=sub_user, user=request.user
                )
                contacts_to_save.append(contact)

                # Processing tags for the contact
                tags = (
                    contact_data.get("Tags").split(" ")
                    if contact_data.get("Tags")
                    else []
                )
                for tag_name in tags:
                    tag = Tag(name=tag_name.strip(), contact=contact)
                    tag.save()

                # Constructing payload for HL
                hl_payload = {
                    "email": filtered_contact_data.get("email"),
                    "phone": filtered_contact_data.get("phone"),
                    "firstName": filtered_contact_data.get("first_name"),
                    "lastName": filtered_contact_data.get("last_name"),
                    "name": f"{filtered_contact_data.get('first_name', '')} {filtered_contact_data.get('last_name', '')}".strip(),
                    "dateOfBirth": filtered_contact_data.get("date_of_birth"),
                    "address1": filtered_contact_data.get("address1"),
                    "city": filtered_contact_data.get("city"),
                    "state": filtered_contact_data.get("state"),
                    "country": filtered_contact_data.get("country"),
                    "postalCode": filtered_contact_data.get("postal_code"),
                    "companyName": filtered_contact_data.get("company_name"),
                    "website": filtered_contact_data.get("website"),
                    "source": filtered_contact_data.get("source"),
                    # If tags are comma-separated in the CSV and stored in a 'tags' field
                    "tags": filtered_contact_data.get("tags").split(" ")
                    if filtered_contact_data.get("tags")
                    else [],
                }

                # Sending data to HL
                url = "https://rest.gohighlevel.com/v1/contacts/"
                headers = {"Authorization": f"Bearer {sub_user.gohighlevel_api_key}"}
                response = requests.post(url, headers=headers, json=hl_payload)
                if response.status_code != 200:
                    return Response(
                        {
                            "error": "Error sending data to GoHighLevel for contact: "
                            + filtered_contact_data.get("first_name")
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Save all contacts in one database hit
            with transaction.atomic():
                Contact.objects.bulk_create(contacts_to_save)
                print("\nSaving contacts to database")
                # Tag.objects.bulk_create(tags_to_save)

            user = request.user
            user.status = "Schedule Calendar"
            user.save()

            print("\ndone....")

            return Response(
                {"message": "Contacts processed and sent to GoHighLevel successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StripeSetupIntentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            setup_intent = stripe.SetupIntent.create()
            return Response(
                {"client_secret": setup_intent.client_secret}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LinkPaymentMethodToCustomer(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Retrieve the Setup Intent ID from the request
        setup_intent_id = request.data.get("setup_intent_id")

        try:
            # Retrieve the logged-in user's SubAccount
            user = request.user.pk
            sub_account = SubAccount.objects.get(user=user)

            # Create a new customer in Stripe using SubAccount details
            customer = stripe.Customer.create(
                email=sub_account.business_email,
                name=f"{sub_account.first_name} {sub_account.last_name}",
                phone=sub_account.contact_phone,
                address={
                    "line1": sub_account.address,
                    "city": sub_account.city,
                    "state": sub_account.state,
                    "postal_code": sub_account.zip_code,
                    "country": sub_account.country,
                },
            )

            print(f"customer created")

            # Retrieve the Setup Intent and Payment Method
            setup_intent = stripe.SetupIntent.retrieve(setup_intent_id)
            payment_method_id = setup_intent.payment_method

            # Attach the Payment Method to the newly created Stripe Customer
            stripe.PaymentMethod.attach(payment_method_id, customer=customer.id)
            print("customer attached")

            # Optionally set it as the default payment method
            stripe.Customer.modify(
                customer.id,
                invoice_settings={"default_payment_method": payment_method_id},
            )

            print("default payment method added")

            url = "https://rest.gohighlevel.com/v1/custom-values/"

            headers = {"Authorization": f"Bearer {sub_account.gohighlevel_api_key}"}

            response = requests.request("GET", url, headers=headers)

            data = json.loads(response.text)

            _id = find_stripe_customer_id(data)

            if _id is None:
                return Response(
                    {"error": "Error creating stripe customer id in GoHighLevel"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            print(f"custom value id is {_id}")

            url = f"https://rest.gohighlevel.com/v1/custom-values/{_id}"

            payload = {"name": "Stripe Customer ID", "value": customer.id}

            response = requests.request("PUT", url, headers=headers, data=payload)

            sub_account.customer_id = customer.id
            sub_account.save()

            if response.status_code == 200:
                user = request.user
                user.status = "Phone Number Purchase"
                user.save()
                return Response(
                    {"status": "Stripe payment method added successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Error creating stripe customer id in GoHighLevel"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InspectionDetailsViewSet(viewsets.ModelViewSet):
    queryset = InspectionDetails.objects.all()
    serializer_class = InspectionDetailsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the logged-in user and their associated SubAccount
        user = request.user
        sub_user = SubAccount.objects.get(user=user.pk)

        # Deserialize the incoming data
        data = request.data
        data["user"] = user.pk
        data["sub_account"] = sub_user.pk
        serializer = self.get_serializer(data=data)

        # Check if the deserialized data is valid
        if serializer.is_valid():
            # Save the CalendarDetails instance with user and sub_user fields set
            serializer.save()

            # Optionally, update the user status
            user.status = "Completed"
            user.save()

            return Response(
                {"message": "Inspection details added successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            # Return an error response if the data is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
