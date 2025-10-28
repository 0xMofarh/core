from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import MainService

# def landing_view(request):
#     """
#     الصفحة الرئيسية للموقع
#     """
#     return render(request, 'main/landing.html')


def home_view(request):
    services = MainService()
    context = services.get_main_data()
    return render(request, 'main/landing.html',context)

def custom_404(request, exception):
    return render(request, 'main/404.html', status=404)

def custom_500(request):
    return render(request, 'main/500.html', status=500)