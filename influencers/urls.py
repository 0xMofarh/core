from django.urls import path
from . import views

app_name = 'influencers'

urlpatterns = [
    # Influencers
    path('', views.influencers_search, name='influencers_search'),
    path('<int:influencer_id>/', views.influencer_detail, name='influencer_detail'),

    path("add/", views.add_influencer, name="add_influencer"),
    path("thank/", views.thank, name="thank"),
    # path('<int:influencer_id>/', views.influencer_detail, name='influencer_detail'),
    
    # # Influencer Management
    # path('add/', views.add_influencer, name='add_influencer'),
    # path('bulk-upload/', views.bulk_upload_influencers, name='bulk_upload_influencers'),
    # path('download-template/', views.download_template, name='download_template'),
    
    # # API endpoints
    # path('api/stats/', views.get_influencer_stats, name='get_influencer_stats'),
    # path('api/test-connection/', views.test_api_connection, name='test_api_connection'),
]
