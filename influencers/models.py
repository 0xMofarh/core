from django.db import models
from django.utils import timezone


class Influencer(models.Model):
    """
    Influencer model
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    licence_number = models.CharField(max_length=100, null=True, blank=True)
    platforms = models.JSONField(null=True, blank=True)   # تحويل JSON string إلى JSONField فعلي
    categories = models.ManyToManyField("Category", related_name="influencers")
    city = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.city or 'Unknown city'})"
    

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

class SocialAccount(models.Model):
    """
    Social media account for an influencer
    """
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('snapchat', 'Snapchat'),
        ('youtube', 'YouTube'),
        ('twitter', 'Twitter'),
    ]

    influencer = models.ForeignKey(
        Influencer,
        on_delete=models.CASCADE,
        related_name='social_accounts'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    username = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    followers_count = models.BigIntegerField(default=0)
    following_count = models.BigIntegerField(default=0)
    heartCount = models.BigIntegerField(default=0)
    videoCount = models.BigIntegerField(default=0)
    engagement_rate_account = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.platform} - {self.username}"


class AccountStat(models.Model):
    """
    Statistics for a social account
    """
    social_account = models.ForeignKey(
        SocialAccount,
        on_delete=models.CASCADE,
        related_name='account_stats'
    )
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_likes_last_10 = models.BigIntegerField(default=0)
    total_comments_last_10 = models.BigIntegerField(default=0)
    total_views_last_10 = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Stat for {self.social_account.username} - {self.engagement_rate or 0}%"


class Post(models.Model):
    """
    Individual post for a social account
    """
    social_account = models.ForeignKey(
        SocialAccount,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    post_url = models.TextField()
    likes = models.BigIntegerField(default=0)
    comments = models.BigIntegerField(default=0)
    views = models.BigIntegerField(default=0)
    share = models.BigIntegerField(default=0)
    download_vidC = models.BigIntegerField(default=0)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Post ({self.social_account.username}) - Likes: {self.likes}"
