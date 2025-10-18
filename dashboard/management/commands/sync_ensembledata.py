from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta
from dashboard.models import Influencer
from dashboard.ensembledata_service import sync_all_influencers, sync_influencer_by_id


class Command(BaseCommand):
    help = 'مزامنة بيانات المؤثرين مع EnsembleData API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--influencer-id',
            type=int,
            help='مزامنة مؤثر محدد (ID)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='إجبار المزامنة حتى لو تمت مؤخراً',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=5,
            help='عدد الأيام المطلوبة لاعتبار البيانات قديمة (افتراضي: 5)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('بدء عملية مزامنة بيانات المؤثرين مع EnsembleData...')
        )
        
        days_threshold = options['days']
        force_sync = options['force']
        influencer_id = options.get('influencer_id')
        
        # إذا تم تحديد مؤثر محدد
        if influencer_id:
            self.sync_single_influencer(influencer_id)
            return
        
        # مزامنة المؤثرين الذين لم يتم مزامنتهم مؤخراً
        if force_sync:
            influencers = Influencer.objects.filter(is_active=True)
            self.stdout.write(f'إجبار مزامنة جميع المؤثرين النشطين ({influencers.count()} مؤثر)')
        else:
            # مؤثرين لم يتم مزامنتهم خلال الأيام المحددة
            cutoff_date = timezone.now() - timedelta(days=days_threshold)
            influencers = Influencer.objects.filter(
                is_active=True
            ).filter(
                models.Q(last_sync__isnull=True) | models.Q(last_sync__lt=cutoff_date)
            )
            
            self.stdout.write(
                f'مزامنة المؤثرين الذين لم يتم مزامنتهم منذ {days_threshold} أيام '
                f'({influencers.count()} مؤثر)'
            )
        
        if influencers.count() == 0:
            self.stdout.write(
                self.style.WARNING('لا توجد مؤثرين يحتاجون للمزامنة')
            )
            return
        
        # بدء المزامنة
        result = sync_all_influencers()
        
        # عرض النتائج
        self.stdout.write(
            self.style.SUCCESS(
                f'تم الانتهاء من المزامنة:\n'
                f'- نجح: {result["synced"]}\n'
                f'- فشل: {result["failed"]}\n'
                f'- المجموع: {result["total"]}'
            )
        )
        
        if result['failed'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'تم فشل {result["failed"]} مزامنة. تحقق من logs للحصول على التفاصيل.'
                )
            )

    def sync_single_influencer(self, influencer_id):
        """مزامنة مؤثر محدد"""
        result = sync_influencer_by_id(influencer_id)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(result['message'])
            )
        else:
            self.stdout.write(
                self.style.ERROR(result['message'])
            )
