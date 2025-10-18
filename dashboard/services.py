from .repositories import DashboardRepository
from django.utils.timezone import now

class DashboardService:
    def __init__(self):
        self.repo = DashboardRepository()

    def get_dashboard_data(self, user):
        user_campaigns = self.repo.get_user_campaigns(user)
        active_campaigns = user_campaigns.filter(status='active')
        
        # عرض آخر 5 حملات نشطة مع بيانات إضافية
        active_campaigns_display = []
        for c in active_campaigns.order_by('-start_date')[:5]:
            days_remaining = (c.end_date - now()).days  # الوقت المتبقي
            active_campaigns_display.append({
                'id': c.id,
                'title': c.title,
                'description': c.description,
                'budget': c.budget,
                'brand': c.brand,
                'participants_count': c.participants.count(),
                'days_remaining': max(days_remaining, 0),
                'start_date': c.start_date,
                'end_date': c.end_date,
            })
        
        context = {
            'user': user,
            'total_campaigns': user_campaigns.count(),
            'total_influencers': self.repo.get_total_influencers(),
            'user_campaigns_count': user_campaigns.count(),
            'active_campaigns_count': active_campaigns.count(),
            'active_campaigns': active_campaigns_display,
        }
        return context
