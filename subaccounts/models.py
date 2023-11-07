from django.db import models


class SubAccount(models.Model):
    appointment_cost = models.IntegerField()
    industry = models.CharField(max_length=200)
    legal_business_name = models.CharField(max_length=200)
    business_name = models.CharField(max_length=252)
    business_region_operation = models.CharField(max_length=252)
    business_email = models.EmailField(unique=True)
    business_phone = models.CharField(max_length=20)
    website = models.TextField()
    has_ein = models.BooleanField(default=False)
    ein = models.CharField(max_length=200, null=True, blank=True)
    business_type = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    country = models.CharField(max_length=200, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    client_number = models.CharField(max_length=20)
    job_position = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    gohighlevel_id = models.CharField(max_length=255, null=True, blank=True)
    gohighlevel_api_key = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.business_name
    

class PurchasedPhoneNumber(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    purchased_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(SubAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.business_name} --> {self.phone_number}"
    

class A2PRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending'
    )
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(SubAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.business_name} --> {self.get_status_display()}"




class Contact(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=250, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    # ForeignKey to SubAccount
    sub_account = models.ForeignKey(SubAccount, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class Tag(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)