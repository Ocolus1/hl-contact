from rest_framework.routers import DefaultRouter
from .views import SubAccountViewSet, ContactViewSet, PhoneNumberViewSet, A2PRegistrationViewSet

router = DefaultRouter()
router.register(r'subaccounts', SubAccountViewSet)
router.register(r'contact', ContactViewSet)
router.register(r'phonenumber', PhoneNumberViewSet)
router.register(r'a2p', A2PRegistrationViewSet)

urlpatterns = router.urls
