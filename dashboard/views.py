from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .services import DashboardService 

@login_required
def dashboard_home(request):
    service = DashboardService()
    context = service.get_dashboard_data(request.user)
    
    print(context)
    return render(request, "dashboard/dashboard_home.html", context)


@login_required
def reports_view(request):
    """
    صفحة التقارير والإحصائيات
    """
    # إحصائيات وهمية للعرض
    context = {
        'total_campaigns': 24,
        'total_influencers': 156,
        'total_reach': 2400000,
        'engagement_rate': 4.2,
    }
    
    return render(request, 'dashboard/reports.html', context)


@login_required
def profile_view(request):
    """
    صفحة الملف الشخصي
    """
    context = {
        'user': request.user,
    }
    
    return render(request, 'dashboard/profile.html', context)


@login_required
def settings_view(request):
    """
    صفحة الإعدادات
    """
    context = {
        'user': request.user,
    }
    
    return render(request, 'dashboard/settings.html', context)