from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # path('', views.landing_view, name='landing'),
    path('', views.home_view, name='home'),
]
