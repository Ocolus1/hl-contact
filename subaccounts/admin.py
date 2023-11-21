from django.contrib import admin
from .models import (
    SubAccount,
    Contact,
    Tag,
    PurchasedPhoneNumber,
    A2PRegistration,
    CustomUser,
    InspectionDetails,
    CalendarDetails,
)

# Register your models here.
admin.site.register(SubAccount)
admin.site.register(Contact)
admin.site.register(PurchasedPhoneNumber)
admin.site.register(Tag)
admin.site.register(A2PRegistration)
admin.site.register(CustomUser)
admin.site.register(InspectionDetails)
admin.site.register(CalendarDetails)
