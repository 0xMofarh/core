from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# def landing_view(request):
#     """
#     الصفحة الرئيسية للموقع
#     """
#     return render(request, 'main/landing.html')


def home_view(request):
    """
    الصفحة الرئيسية للمستخدمين المسجلين
    """
    return render(request, 'main/landing.html')

def custom_404(request, exception):
    return render(request, 'main/404.html', status=404)

def custom_500(request):
    return render(request, 'main/500.html', status=500)