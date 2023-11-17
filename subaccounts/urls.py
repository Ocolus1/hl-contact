from rest_framework.routers import DefaultRouter
from .views import SubAccountViewSet, ContactViewSet, PhoneNumberViewSet, A2PRegistrationViewSet, StripeSetupIntentAPIView, LinkPaymentMethodToCustomer
from django.urls import path, include

router = DefaultRouter()
router.register(r'subaccounts', SubAccountViewSet)
router.register(r'contact', ContactViewSet)
router.register(r'phonenumber', PhoneNumberViewSet)
router.register(r'a2p', A2PRegistrationViewSet)


urlpatterns = [
    path('stripe-setup-intent/', StripeSetupIntentAPIView.as_view(), name='stripe-setup-intent'),
    path('link-payment-method/', LinkPaymentMethodToCustomer.as_view(), name='link-payment-method'),
    path('', include(router.urls)),
]
