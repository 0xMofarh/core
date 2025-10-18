from django.contrib import admin
from .models import Campaign, CampaignParticipant, Platform


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'brand', 'campaign_type', 'status', 'budget', 'created_by', 'created_at']
    list_filter = ['status', 'campaign_type', 'created_at', 'start_date', 'end_date']
    search_fields = ['title', 'brand', 'description', 'target_audience']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('معلومات الحملة', {
            'fields': ('title', 'description', 'brand', 'campaign_type')
        }),
        ('التفاصيل المالية', {
            'fields': ('budget', 'target_audience')
        }),
        ('التواريخ', {
            'fields': ('start_date', 'end_date')
        }),
        ('الحالة والمؤسس', {
            'fields': ('status', 'created_by')
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CampaignParticipant)
class CampaignParticipantAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'influencer', 'status', 'proposed_price', 'applied_at']
    list_filter = ['status', 'applied_at', 'accepted_at']
    search_fields = ['campaign__title', 'influencer__name']
    readonly_fields = ['applied_at', 'accepted_at', 'completed_at']


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    list_filter = ['is_active']