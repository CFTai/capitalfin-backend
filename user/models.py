from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    PENDING = 1
    VERIFIED = 2
    REJECTED = 3
    REVERTED = 4
    UNVERIFIED = 5
    USER_STATUS = [
        (1, "pending"),
        (2, "verified"),
        (3, "rejected"),
        (4, "reverted"),
        (5, "unverified"),
    ]

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    fullname_pinyin = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(choices=USER_STATUS, default=UNVERIFIED)
    remark = models.TextField(null=True, blank=True)
    password = models.CharField(max_length=128)
    transaction_password = models.CharField(max_length=128)

    objects = UserManager()

    USERNAME_FIELD = "username"

    class Meta:
        db_table = "user"
        ordering = ["id"]


class UserDetails(models.Model):
    MALE = "M"
    FEMALE = "F"
    GENDER = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    national_id = models.CharField(max_length=100, null=True)
    nationality = models.CharField(max_length=5, null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(choices=GENDER, max_length=100, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="details")

    class Meta:
        db_table = "user_details"
        ordering = ["id"]


class UserContact(models.Model):
    country = models.CharField(max_length=5)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=5)
    contact_no = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="contact")

    class Meta:
        db_table = "user_contacts"
        ordering = ["id"]


class UserAttachments(models.Model):
    upload = models.OneToOneField(
        "upload.Upload",
        on_delete=models.CASCADE,
        related_name="user_attachment",
        unique=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attachments")

    class Meta:
        db_table = "user_attachments"
        ordering = ["id"]
