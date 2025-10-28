from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Influencer, SocialAccount, Category
from .services import InfluencerService

@login_required
def influencers_search(request):
    filters = {
        "search": request.GET.get("search", ""),
        "city": request.GET.get("city", ""),
        "gender": request.GET.get("gender", ""),
        "platform": request.GET.get("platform", ""),
        "followers_min": request.GET.get("followers_min"),
        "followers_max": request.GET.get("followers_max"),
        "categories": request.GET.getlist("categories"),
        "sort_by": request.GET.get("sort_by", "id"),
    }
    page_number = request.GET.get("page", 1)
    print("🔍 Category filter:", request.GET.get("categories"))

    service = InfluencerService()
    data = service.search_influencers(filters, page_number)

    return render(request, "influencers/influencers_search.html", data)

@login_required
def add_influencer(request):
    if request.method == "POST":
        service = InfluencerService()
        return service.add_influencer(request)
    return render(request, "influencers/influencer_form.html")

def thank(request):
    return render(request, "influencers/thank_you.html")


@login_required
def influencer_detail(request, influencer_id):
    service = InfluencerService()
    influencer = service.get_influencer_detail(influencer_id)
    
    return render(request, "influencers/influencer_detail.html", {
        "influencer": influencer
    })
