from django.contrib import admin
from .models import Influencer, SocialAccount, AccountStat, Post


@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "gender",
        "city",
        "licence_number",
        "created_at",
    )
    list_filter = ("gender", "city", "created_at")
    search_fields = ("name", "email", "licence_number", "city")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {
            "fields": ("name", "gender", "avatar", "licence_number", "platforms", "categories", "city")
        }),
        ("Metadata", {
            "fields": ("created_at",)
        }),
    )


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "platform",
        "username",
        "influencer",
        "followers_count",
        "is_verified",
        "created_at",
    )
    list_filter = ("platform", "is_verified", "created_at")
    search_fields = ("username", "platform", "influencer__name")
    ordering = ("-created_at",)


@admin.register(AccountStat)
class AccountStatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "social_account",
        "engagement_rate",
        "total_likes_last_10",
        "total_comments_last_10",
        "total_views_last_10",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("social_account__username",)
    ordering = ("-created_at",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "social_account",
        "post_url",
        "likes",
        "comments",
        "views",
        "engagement_rate",
        "posted_at",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("social_account__username", "post_url")
    ordering = ("-created_at",)
