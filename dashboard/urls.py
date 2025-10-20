from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('influencers/', lambda request: redirect('influencers:influencers_search')),
    path('/campaigns/', lambda request: redirect('campaigns:campaigns_list')),
    path('reports/', views.reports_view, name='reports'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
]
