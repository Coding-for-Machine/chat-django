from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random
import string

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None):
        if not phone_number:
            raise ValueError('Users must have a phone number')

        user = self.model(
            phone_number=phone_number,
        )
        
        user.set_unusable_password()  # No password, because OTP will be used
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number=phone_number,
        )
        user.is_staff = True
        user.is_superuser = True
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    
class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=13, unique=True)  # '+998' bilan
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

    # Helper function to generate OTP code
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))  # 6 digit OTP code

class OTPCodeSession(models.Model):
    phone_number = models.CharField(max_length=15)  # Telefon raqami
    code = models.CharField(max_length=6)  # Kod
    secret = models.CharField(max_length=100, default="ui")  # secretni saqlash uchun
    created_at = models.DateTimeField(auto_now_add=True)  # Yaratilgan sana
    updated_at = models.DateTimeField(auto_now=True)  # Yangilangan sana

    def __str__(self):
        return f'{self.phone_number} - {self.code}'