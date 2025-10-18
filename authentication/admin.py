from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, OTP, Payment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser
    """
    list_display = ('email', 'full_name', 'mobile_number', 'package', 'is_email_verified', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_email_verified', 'is_active', 'is_staff', 'package', 'date_joined')
    search_fields = ('email', 'full_name', 'mobile_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'mobile_number', 'package')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Verification', {'fields': ('is_email_verified',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'mobile_number', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """
    Admin configuration for OTP
    """
    list_display = ('user', 'code', 'purpose', 'is_verified', 'created_at', 'expires_at', 'is_expired_display')
    list_filter = ('purpose', 'is_verified', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'expires_at', 'is_expired_display')
    
    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Payment
    """
    list_display = ('user', 'package', 'amount_display', 'payment_status', 'transaction_id', 'payment_date', 'created_at')
    list_filter = ('payment_status', 'package', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def amount_display(self, obj):
        return obj.get_amount_display()
    amount_display.short_description = 'Amount'