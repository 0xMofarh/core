from django.urls import path
from . import views

app_name = 'influencers'

urlpatterns = [
    # Influencers
    path('', views.influencers_search, name='influencers_search'),
    path('<int:influencer_id>/', views.influencer_detail, name='influencer_detail'),

    path("add/", views.add_influencer, name="add_influencer"),
    path("thank/", views.thank, name="thank"),

]
