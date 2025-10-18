from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
import random
import string
from datetime import timedelta


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for CustomUser model
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User model extending AbstractUser
    """
    PACKAGE_CHOICES = [
        ('free_trial', 'Free Trial - 7 days'),
        ('monthly', 'Monthly - 299 SAR'),
    ]
    
    # Remove username field and use email as primary identifier
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    
    # Additional fields
    full_name = models.CharField(max_length=255, verbose_name="Full Name")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    mobile_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Mobile Number"
    )
    
    package = models.CharField(
        max_length=20,
        choices=PACKAGE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Package"
    )
    
    is_email_verified = models.BooleanField(default=False, verbose_name="Email Verified")
    
    # Override date_joined to use our custom field
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Last Login")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile_number']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class OTP(models.Model):
    """
    OTP model for email verification
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6, verbose_name="OTP Code")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    expires_at = models.DateTimeField(verbose_name="Expires At")
    is_verified = models.BooleanField(default=False, verbose_name="Is Verified")
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('registration', 'Registration'),
            ('password_reset', 'Password Reset'),
        ],
        default='registration',
        verbose_name="Purpose"
    )

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.email}: {self.code}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_expired() and not self.is_verified

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def create_otp(user, purpose='registration'):
        # Deactivate previous OTPs for this user
        OTP.objects.filter(user=user, is_verified=False).update(is_verified=True)
        
        # Create new OTP
        code = OTP.generate_code()
        otp = OTP.objects.create(
            user=user,
            code=code,
            purpose=purpose
        )
        return otp

class PasswordResetCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)  # كود 6 أرقام
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class Payment(models.Model):
    """
    Payment model for package subscriptions
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')
    package = models.CharField(max_length=20, choices=CustomUser.PACKAGE_CHOICES, verbose_name="Package")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name="Payment Status"
    )
    transaction_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Transaction ID")
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Payment Date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for {self.user.email} - {self.package} ({self.payment_status})"

    def get_amount_display(self):
        if self.package == 'free_trial':
            return 'Free'
        return f"{self.amount} SAR"