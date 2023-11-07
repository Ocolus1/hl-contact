from rest_framework import serializers
from .models import SubAccount, PurchasedPhoneNumber, A2PRegistration, Contact

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