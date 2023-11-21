from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=250, blank=True, null=True, default="User Info"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


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
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.business_name


class CalendarDetails(models.Model):
    bookingMethod = models.CharField(max_length=200)
    email = models.CharField(max_length=200, null=True, blank=True)
    days = models.JSONField(null=True)
    timezone = models.CharField(max_length=200)
    inspectionDuration = models.CharField(max_length=200)
    timeBuffer = models.CharField(max_length=252)
    appointmentReminder = models.CharField(max_length=252)
    notificationPreference = models.CharField(max_length=200, null=True, blank=True)
    notificationPhoneNumber = models.CharField(max_length=200, null=True, blank=True)
    notificationEmail = models.CharField(max_length=200, null=True, blank=True)
    sub_account = models.ForeignKey(SubAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.sub_account.business_name


class PurchasedPhoneNumber(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    purchased_on = models.DateTimeField(auto_now_add=True)
    sub_account = models.ForeignKey(SubAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sub_account.business_name} --> {self.phone_number}"


class A2PRegistration(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    last_updated = models.DateTimeField(auto_now=True)
    sub_account = models.ForeignKey(SubAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sub_account.business_name} --> {self.get_status_display()}"


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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class Tag(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)


class InspectionDetails(models.Model):
    moreInspections = models.IntegerField(null=True, blank=True) 
    jobCapacity = models.IntegerField(null=True, blank=True)
    averageJobs = models.IntegerField(null=True, blank=True)
    paymentMethod = models.CharField(max_length=100, blank=True)
    completionTime = models.IntegerField(null=True, blank=True) 
    supplyCostsIncreasing = models.CharField(max_length=10, blank=True) 
    priceIncreaseLower = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    priceIncreaseUpper = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    offer = models.JSONField(null=True)  
    messageSender = models.CharField(max_length=100, blank=True)
    sub_account = models.ForeignKey(SubAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.messageSender} - {self.moreInspections} inspections"
