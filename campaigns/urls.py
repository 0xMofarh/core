from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Campaigns
    path('', views.campaigns_list, name='campaigns_list'),
    path('<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    
    # Campaign Management
    path('create/', views.create_campaign, name='create_campaign'),
    path('<int:campaign_id>/edit/', views.edit_campaign, name='edit_campaign'),
    path('<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),

    
    path('<int:campaign_id>/add-participant/', views.add_participant, name='add_participant'),
    path('<int:campaign_id>/remove-participant/<int:influencer_id>/', views.remove_participant_view, name='remove_participant'),
    path('<int:campaign_id>/accept-participant/<int:influencer_id>/', views.accept_participant_view, name='accept_participant'),

    # # API endpoints
    path('api/<int:campaign_id>/add-participant/', views.add_participant_api, name='add_participant_api'),
    path('api/campaigns-list/', views.campaigns_list_api, name='campaigns_list_api'),

]
