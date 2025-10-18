from django.shortcuts import get_object_or_404
from .models import Campaign, CampaignParticipant
from influencers.models import Influencer


class CampaignRepository:
    def get_user_campaigns(self, user):
        return Campaign.objects.filter(created_by=user).order_by('-created_at')

    def filter_by_status(self, campaigns, status):
        if status:
            return campaigns.filter(status=status)
        return campaigns

    def get_user_campaign_by_id(self, campaign_id, user):
        return get_object_or_404(Campaign, id=campaign_id, created_by=user)
    
    def get_campaign_by_id(self, campaign_id, user=None):

        qs = Campaign.objects
        if user:
            qs = qs.filter(created_by=user)
        return get_object_or_404(qs, id=campaign_id)
    def get_participants_for_campaign(self, campaign):
        return campaign.participants.select_related('influencer')

    def create_campaign(self, data, user):
        """إنشاء حملة جديدة"""
        return Campaign.objects.create(
            title=data.get('title'),
            description=data.get('description'),
            brand=data.get('brand'),
            campaign_type=data.get('campaign_type'),
            budget=data.get('budget'),
            target_audience=data.get('target_audience'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            created_by=user
        )

    def update_campaign(self, campaign, data):
        """تحديث بيانات الحملة"""
        campaign.title = data.get('title')
        campaign.description = data.get('description')
        campaign.brand = data.get('brand')
        campaign.campaign_type = data.get('campaign_type')
        campaign.budget = data.get('budget')
        campaign.target_audience = data.get('target_audience')
        campaign.start_date = data.get('start_date')
        campaign.end_date = data.get('end_date')
        campaign.status = data.get('status')
        campaign.save()
        return campaign

    def get_campaign_model(self):
        return Campaign

    def delete_campaign(self, campaign):

        campaign.delete()
        return True
    
    def add_participant(self, campaign, influencer, proposed_price=None, deliverables=None):
        """إضافة مؤثر للحملة"""
        participant, created = CampaignParticipant.objects.get_or_create(
            campaign=campaign,
            influencer=influencer,
            defaults={
                'proposed_price': proposed_price,
                'deliverables': deliverables,
            }
        )
        return participant, created
    def get_active_campaigns(self, limit=5):
        """إرجاع آخر 5 حملات نشطة"""
        return (
            Campaign.objects.filter(status="active")
            .order_by("-created_at")[:limit]
        )
class InfluencerRepository:
    def get_active_influencers(self):
        return Influencer.objects.all()

    def get_influencer_by_id(self, influencer_id):
        return get_object_or_404(Influencer, id=influencer_id)


class CampaignParticipantRepository:


    def add_participant(self, campaign, influencer, proposed_price, deliverables):
        participant, created = CampaignParticipant.objects.get_or_create(
            campaign=campaign,
            influencer=influencer,
            defaults={
                'proposed_price': proposed_price,
                'deliverables': deliverables,
            }
        )
        return participant, created
    
    def remove_participant(self, campaign, influencer):
        """
        يحذف صف المشاركة إذا وجد
        """
        try:
            participant = CampaignParticipant.objects.get(campaign=campaign, influencer=influencer)
            participant.delete()
            return True
        except CampaignParticipant.DoesNotExist:
            return False


    def get_participant(self, campaign, influencer):
        try:
            return CampaignParticipant.objects.get(campaign=campaign, influencer=influencer)
        except CampaignParticipant.DoesNotExist:
            return None