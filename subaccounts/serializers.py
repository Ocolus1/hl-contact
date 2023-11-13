from rest_framework import serializers
from .models import SubAccount, PurchasedPhoneNumber, A2PRegistration, Contact
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer


class CustomRegisterSerializer(RegisterSerializer):
    username = None  # Exclude username
    password2 = None  # Exclude password2

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict.pop('username', None)  # Remove username from cleaned data
        data_dict.pop('password2', None)  # Remove username from cleaned data
        return data_dict
    

class CustomLoginSerializer(LoginSerializer):
    username = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)


class SubAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubAccount
        fields = '__all__'


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedPhoneNumber
        fields = '__all__'


class A2PRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = A2PRegistration
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'