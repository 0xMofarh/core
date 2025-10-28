from influencers.models import Influencer
from campaigns.models import Campaign
from authentication.models import CustomUser
class MainRepository:
    def get_total_influencers(self):
        return Influencer.objects.count()
    
    def get_total_campaing(self):
        return Campaign.objects.count()
    
    def get_total_users(self):
        return CustomUser.objects.count()