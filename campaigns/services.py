from django.contrib import messages
from django.shortcuts import redirect
from .repositories import (
    CampaignRepository,
    InfluencerRepository,
    CampaignParticipantRepository)

class CampaignService:
    def __init__(self):
        self.repo = CampaignRepository()


    def list_campaigns(self, user, filters, page_number, per_page=10):
        campaigns = self.repo.get_user_campaigns(user)
        campaigns = self.repo.filter_by_status(campaigns, filters.get('status'))
        from django.core.paginator import Paginator
        paginator = Paginator(campaigns, per_page)
        page_obj = paginator.get_page(page_number)
        return {
            'page_obj': page_obj,
            'campaigns': page_obj,
            'status_filter': filters.get('status'),
        }

    def get_campaign_details(self, user, campaign_id):
        campaign = self.repo.get_user_campaign_by_id(campaign_id, user)
        participants = self.repo.get_participants_for_campaign(campaign)
        return {'campaign': campaign, 'participants': participants}

    def create_campaign(self, request):
        """منطق إنشاء الحملة"""
        try:
            campaign = self.repo.create_campaign(request.POST, request.user)
            messages.success(request, f'تم إنشاء الحملة {campaign.title} بنجاح!')
            return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء الحملة: {str(e)}')
            return None

    def edit_campaign(self, request, campaign_id):
        """منطق تعديل الحملة"""
        campaign = self.repo.get_user_campaign_by_id(campaign_id, request.user)
        try:
            self.repo.update_campaign(campaign, request.POST)
            messages.success(request, f'تم تحديث الحملة {campaign.title} بنجاح!')
            return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث الحملة: {str(e)}')
            return None
        
    def delete_campaign(self, campaign_id, user):
        """
        حذف الحملة لو كانت تابعة للمستخدم الحالي
        """
        campaign = self.repo.get_campaign_by_id(campaign_id, user)
        self.repo.delete_campaign(campaign)
        return True
    
    def get_latest_active_campaigns(self, limit=5):
        return self.repo.get_active_campaigns(limit)

class CampaignParticipantService:
    def __init__(self):
        self.campaign_repo = CampaignRepository()
        self.influencer_repo = InfluencerRepository()
        self.participant_repo = CampaignParticipantRepository()

    def add_participant(self, request, campaign_id):
        campaign = self.campaign_repo.get_campaign_by_id(campaign_id, request.user)
        influencer_id = request.POST.get('influencer_id')
        proposed_price = request.POST.get('proposed_price')
        deliverables = request.POST.get('deliverables')

        influencer = self.influencer_repo.get_influencer_by_id(influencer_id)
        participant, created = self.participant_repo.add_participant(
            campaign, influencer, proposed_price, deliverables
        )

        if created:
            messages.success(request, f'تم إضافة {influencer.name} إلى الحملة بنجاح!')
        else:
            messages.warning(request, f'{influencer.name} موجود بالفعل في هذه الحملة')

        return campaign

    def get_available_influencers(self):
        return self.influencer_repo.get_active_influencers()
    
    def remove_participant(self, request, campaign_id, influencer_id):
        """
        حذف مؤثر من الحملة
        """
        campaign = self.campaign_repo.get_campaign_by_id(campaign_id, request.user)
        influencer = self.influencer_repo.get_influencer_by_id(influencer_id)
        
        removed = self.participant_repo.remove_participant(campaign, influencer)
        
        if removed:
            messages.success(request, f"تم إزالة {influencer.name} من الحملة بنجاح ✅")
        else:
            messages.warning(request, f"{influencer.name} غير موجود في هذه الحملة")
        
        return campaign
    

    def accept_participant(self, request, campaign_id, influencer_id):
        """
        تغيير حالة مشاركة المؤثر إلى 'مقبول'
        """
        campaign = self.campaign_repo.get_campaign_by_id(campaign_id, request.user)
        influencer = self.influencer_repo.get_influencer_by_id(influencer_id)

        participant = self.participant_repo.get_participant(campaign, influencer)
        if participant:
            participant.status = 'accepted'  # أو أي قيمة عندك في STATUS_CHOICES
            participant.save()
            messages.success(request, f"تم قبول {influencer.name} في الحملة ✅")
            return True
        else:
            messages.warning(request, f"{influencer.name} غير موجود في هذه الحملة")
            return False