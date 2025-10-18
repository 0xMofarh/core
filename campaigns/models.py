from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Campaign(models.Model):
    """
    نموذج الحملات التسويقية
    """
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('active', 'نشطة'),
        ('paused', 'متوقفة'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغاة'),
    ]
    
    CAMPAIGN_TYPE_CHOICES = [
        ('product_launch', 'إطلاق منتج'),
        ('brand_awareness', 'التوعية بالعلامة التجارية'),
        ('promotion', 'ترويج'),
        ('event', 'فعالية'),
        ('collaboration', 'تعاون'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="عنوان الحملة")
    description = models.TextField(verbose_name="وصف الحملة")
    brand = models.CharField(max_length=100, verbose_name="العلامة التجارية")
    
    # معلومات الحملة
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES, verbose_name="نوع الحملة")
    budget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الميزانية")
    target_audience = models.CharField(max_length=200, verbose_name="الجمهور المستهدف")
    
    # التواريخ
    start_date = models.DateTimeField(verbose_name="تاريخ البداية")
    end_date = models.DateTimeField(verbose_name="تاريخ النهاية")
    
    # الحالة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    
    # المؤسس
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_campaigns', verbose_name="أنشأها")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "حملة"
        verbose_name_plural = "الحملات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.brand}"
    
    def is_active(self):
        """فحص إذا كانت الحملة نشطة حالياً"""
        now = timezone.now()
        return (self.status == 'active' and 
                self.start_date <= now <= self.end_date)
    
    def days_remaining(self):
        """عدد الأيام المتبقية"""
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0
    
    def get_participating_influencers_count(self):
        """عدد المؤثرين المشاركين في الحملة"""
        return self.participants.filter(is_accepted=True).count()


class CampaignParticipant(models.Model):
    """
    نموذج مشاركة المؤثرين في الحملات
    """
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('accepted', 'مقبول'),
        ('rejected', 'مرفوض'),
        ('completed', 'مكتمل'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='participants', verbose_name="الحملة")
    influencer = models.ForeignKey('influencers.Influencer', on_delete=models.CASCADE, related_name='campaign_participations', verbose_name="المؤثر")
    
    # معلومات المشاركة
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="السعر المقترح",null=True, blank=True)
    deliverables = models.TextField(default="سيتم تحديد التسليمات لاحقاً", verbose_name="التسليمات المطلوبة",null=True, blank=True)
    
    # الحالة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    is_accepted = models.BooleanField(default=False, verbose_name="مقبول")
    
    # التواريخ
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقديم")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ القبول")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإنجاز")
    
    class Meta:
        verbose_name = "مشارك في الحملة"
        verbose_name_plural = "مشاركو الحملات"
        unique_together = ['campaign', 'influencer']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.influencer.name} - {self.campaign.title}"


class Platform(models.Model):
    """
    نموذج المنصات الاجتماعية
    """
    name = models.CharField(max_length=50, verbose_name="اسم المنصة")
    icon = models.CharField(max_length=50, verbose_name="أيقونة المنصة")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    
    class Meta:
        verbose_name = "منصة"
        verbose_name_plural = "المنصات"
    
    def __str__(self):
        return self.name