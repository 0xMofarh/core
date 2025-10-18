from campaigns.models import Campaign
from django.contrib.auth import get_user_model
from datetime import date
from influencers.models import Influencer

User = get_user_model()
class DashboardRepository:
    def get_user_campaigns(self, user):
        return Campaign.objects.filter(created_by=user)

    def get_active_campaigns(self, user):
        today = date.today()
        return self.get_user_campaigns(user).filter(end_date__gte=today)

    def get_total_influencers(self):
        return Influencer.objects.count()