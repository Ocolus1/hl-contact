from django.db import transaction
import math
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SubAccount, PurchasedPhoneNumber, A2PRegistration, Contact, Tag
from .serializers import SubAccountSerializer, PhoneNumberSerializer, ContactSerializer, A2PRegistrationSerializer
from drf_yasg.utils import swagger_auto_schema
import requests
from django.conf import settings
from .utils import generate_dynamic_mapping, buy_phone_number_with_retries, a2pregister_with_retries


class SubAccountViewSet(viewsets.ModelViewSet):
    queryset = SubAccount.objects.all()
    serializer_class = SubAccountSerializer

    @swagger_auto_schema(operation_description="Create a new SubAccount and send data to GoHighLevel.")
    @action(detail=False, methods=['POST'])
    def create_subaccount(self, request):
        serializer = self.get_serializer(data=request.data)

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
                "snapshot": { "id": "FzxccDUD3xd34OLELmnT", "type": "own" }
            }

            # Send data to GoHighLevel
            url = "https://rest.gohighlevel.com/v1/locations/"
            headers = {
                'Authorization': f'Bearer {settings.TOKEN}'
            }
            response = requests.post(url, headers=headers, json=gohighlevel_payload)
            if response.status_code == 200:
                response_data = response.json()
                sub_account.gohighlevel_id = response_data.get('id')
                sub_account.gohighlevel_api_key = response_data.get('apiKey')
                sub_account.save()  # Update the SubAccount instance with the new data
                return Response({"message": "Subaccount created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Error creating subaccount in GoHighLevel"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PhoneNumberViewSet(viewsets.ModelViewSet):
    queryset = PurchasedPhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer

    @swagger_auto_schema(operation_description="Buy a new Phone NUmber from GoHighLevel.")
    @action(detail=False, methods=['POST'])
    def purchase_phone_number(self, request):
        business_email = request.data.get('businessEmail')
        sub_user = SubAccount.objects.get(business_email=business_email)

        if sub_user:
            phone = buy_phone_number_with_retries(sub_user.business_name, sub_user.business_phone)

            if phone:
                PurchasedPhoneNumber.objects.create(phone_number=phone, user=sub_user)
                return Response({"message": "Phone Number purchased successfully"}, status=status.HTTP_201_CREATED)
            
            return Response({"error": "Error purchasing number from GoHighLevel. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Error purchasing number from GoHighLevel. Please try again."}, status=status.HTTP_400_BAD_REQUEST)


class A2PRegistrationViewSet(viewsets.ModelViewSet):
    queryset = A2PRegistration.objects.all()
    serializer_class = A2PRegistrationSerializer

    @swagger_auto_schema(operation_description="A2PRegistration on  GoHighLevel.")
    @action(detail=False, methods=['POST'])
    def A2PRegistration(self, request):
        business_email = request.data.get('businessEmail')
        sub_user = SubAccount.objects.get(business_email=business_email)

        if sub_user:
            try:
                stats = a2pregister_with_retries(sub_user)
                
                if stats:

                    A2PRegistration.objects.create(status="pending", user=sub_user)

                    return Response({"message": "A2PRegistration completed successfully"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "Error completing A2PRegistration on GoHighLevel. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error": "Error completing A2PRegistration on GoHighLevel. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Error completing A2PRegistration on GoHighLevel. Please try again."}, status=status.HTTP_400_BAD_REQUEST)



class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(operation_description="Upload CSV, clean data, and send to GoHighLevel.")
    @action(detail=False, methods=['POST'])
    def upload_and_process(self, request):
        csv_file = request.FILES.get('csv_file')
        business_email = request.data.get('business_email')

        # Get the SubAccount instance
        sub_account = SubAccount.objects.get(business_email=business_email)
        
        # Read CSV using pandas
        df = pd.read_csv(csv_file)

        # Cleaning logic
        # Remove people with the main company’s domain in their email address
        if 'Primary Contact: website' in df.columns:
            for domain in df['Primary Contact: website'].dropna():
                domain = domain.replace('www.', '')  # removing 'www.' if it's there
                mask = ~df['Primary Contact: Email'].str.endswith(domain)
                df = df[mask]

        # Drop empty columns and rows
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)

        # Get the column names from the CSV
        csv_columns = df.columns.tolist()

        # Get the Django model field names
        model_fields = [field.name for field in Contact._meta.fields]

        # Generate the dynamic mapping
        CSV_TO_MODEL_MAPPING = generate_dynamic_mapping(csv_columns, model_fields)

        # Determine the columns for names, emails, and phone based on the mapping
        first_name_column = next((csv_col for csv_col, model_field in CSV_TO_MODEL_MAPPING.items() if model_field == 'first_name'), None)
        last_name_column = next((csv_col for csv_col, model_field in CSV_TO_MODEL_MAPPING.items() if model_field == 'last_name'), None)
        email_column = next((csv_col for csv_col, model_field in CSV_TO_MODEL_MAPPING.items() if model_field == 'email'), None)
        name_column = next((csv_col for csv_col, model_field in CSV_TO_MODEL_MAPPING.items() if model_field == 'name'), None)
        phone_column = next((csv_col for csv_col, model_field in CSV_TO_MODEL_MAPPING.items() if model_field == 'phone'), None)

        # Check if columns exist in the DataFrame and apply transformations
        if first_name_column in df.columns:
            df[first_name_column] = df[first_name_column].str.title()
            df = df[~df[first_name_column].str.contains('test', case=False, na=False)]

        if last_name_column in df.columns:
            df[last_name_column] = df[last_name_column].str.title()
            df = df[~df[last_name_column].str.contains('test', case=False, na=False)]

        # If there's no separate first and last name, but there's a combined name column
        if name_column in df.columns:
            df[name_column] = df[name_column].str.title()
            df = df[~df[name_column].str.contains('test', case=False, na=False)]

        # Remove any email that has the word 'test' in it
        if email_column in df.columns:
            df = df[~df[email_column].str.contains('test', case=False, na=False)]

        # Remove rows without both email and phone values
        if email_column in df.columns and phone_column in df.columns:
            df = df[df[email_column].notna() | df[phone_column].notna()]


        # Convert DataFrame back to a list of dictionaries for processing
        contacts_list = df.to_dict(orient='records')

        contacts_to_save = []


        for contact_data in contacts_list:
            # Filter out unwanted columns based on our mapping
            filtered_contact_data = {CSV_TO_MODEL_MAPPING[key]: value for key, value in contact_data.items() if key in CSV_TO_MODEL_MAPPING}
            # Remove keys with nan values
            filtered_contact_data = {k: v.strip() if isinstance(v, str) else v for k, v in filtered_contact_data.items() if not isinstance(v, float) or not math.isnan(v)}

            # Now, create a Contact instance using the filtered data
            contact = Contact(**filtered_contact_data, sub_account=sub_account)
            contacts_to_save.append(contact)

            # Processing tags for the contact
            tags = contact_data.get('Tags').split(" ") if contact_data.get('Tags') else []
            for tag_name in tags:
                tag = Tag(name=tag_name.strip(), contact=contact)
                tag.save()

            # Constructing payload for HL
            hl_payload = {
                "email": filtered_contact_data.get('email'),
                "phone": filtered_contact_data.get('phone'),
                "firstName": filtered_contact_data.get('first_name'),
                "lastName": filtered_contact_data.get('last_name'),
                "name": f"{filtered_contact_data.get('first_name', '')} {filtered_contact_data.get('last_name', '')}".strip(),
                "dateOfBirth": filtered_contact_data.get('date_of_birth'),
                "address1": filtered_contact_data.get('address1'),
                "city": filtered_contact_data.get('city'),
                "state": filtered_contact_data.get('state'),
                "country": filtered_contact_data.get('country'),
                "postalCode": filtered_contact_data.get('postal_code'),
                "companyName": filtered_contact_data.get('company_name'),
                "website": filtered_contact_data.get('website'),
                "source": filtered_contact_data.get('source'),
                # If tags are comma-separated in the CSV and stored in a 'tags' field
                "tags": filtered_contact_data.get('tags').split(" ") if filtered_contact_data.get('tags') else [],
            }


            # Sending data to HL
            url = "https://rest.gohighlevel.com/v1/contacts/"
            headers = {
                'Authorization': f'Bearer {sub_account.gohighlevel_api_key}'
            }
            response = requests.post(url, headers=headers, json=hl_payload)
            if response.status_code != 200:
                return Response({"error": "Error sending data to GoHighLevel for contact: " + filtered_contact_data.get('first_name')}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save all contacts in one database hit
        with transaction.atomic():
            Contact.objects.bulk_create(contacts_to_save)
            # Tag.objects.bulk_create(tags_to_save)

        return Response({"message": "Contacts processed and sent to GoHighLevel successfully"}, status=status.HTTP_201_CREATED)
