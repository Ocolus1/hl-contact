from django.contrib import admin
from .models import SubAccount, Contact, Tag, PurchasedPhoneNumber, A2PRegistration

# Register your models here.
admin.site.register(SubAccount)
admin.site.register(Contact)
admin.site.register(PurchasedPhoneNumber)
admin.site.register(Tag)
admin.site.register(A2PRegistration)