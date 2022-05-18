from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, user_name, password, **other_fields):
        if not email:
            raise ValueError("You must provide an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, user_name, password, **other_fields):
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        other_fields.setdefault("is_staff", True)
        if other_fields.get("is_superuser") is not True:
            raise ValueError("SuperUser must be assigned to is_superuser=True")
        if other_fields.get("is_staff") is not True:
            raise ValueError("SuperUser must be assigned to is_staff=True")
        return self.create_user(email, user_name, password, **other_fields)


class Users(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_in_insulin_therapy = models.BooleanField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    first_login = models.BooleanField(default=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.user_name
