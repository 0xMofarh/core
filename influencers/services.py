from .repositories import InfluencerRepository
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect

class InfluencerService:
    def __init__(self):
        self.repo = InfluencerRepository()

    def search_influencers(self, filters, page_number, per_page=9):
        queryset = self.repo.get_all()
        queryset = self.repo.filter_by_name(queryset, filters.get("search"))
        queryset = self.repo.filter_by_city(queryset, filters.get("city"))
        queryset = self.repo.filter_by_gender(queryset, filters.get("gender"))
        queryset = self.repo.filter_by_platform(queryset, filters.get("platform"))
        queryset = self.repo.filter_by_followers(
            queryset,
            filters.get("followers_min"),
            filters.get("followers_max")
        )
        queryset = self.repo.order_by(queryset, filters.get("sort_by", "id"))

        # تجهيز البيانات النهائية مع الحسابات والإحصائيات
        influencers_data = []
        for inf in queryset:
            accounts = inf.social_accounts.all()
            accounts_data = [
                {
                    "platform": acc.platform,
                    "username": acc.username,
                    "followers_count": acc.followers_count,
                    "engagement_rate_account": acc.engagement_rate_account,
                    "is_verified": acc.is_verified,
                }
                for acc in accounts
            ]
            total_followers = sum(acc["followers_count"] for acc in accounts_data)
            influencers_data.append({
                "id": inf.id,
                "name": inf.name,
                "city": inf.city,
                "gender": inf.gender,
                "avatar": inf.avatar,
                "social_accounts": accounts_data,
                "total_followers": total_followers,
                "created_at": inf.created_at,
            })

        paginator = Paginator(influencers_data, per_page)
        page_obj = paginator.get_page(page_number)

        return {
            "page_obj": page_obj,
            "filters": filters,
            "cities": self.repo.get_cities(),
            "platforms": self.repo.get_platforms()
        }

    def add_influencer(self, request):
        name = request.POST.get("name")
        gender = request.POST.get("gender")
        verified_id = request.POST.get("verified_id")
        contact_phone = request.POST.get("contact_phone")
        city = request.POST.get("city")
        categories = request.POST.getlist("categories")

        influencer = self.repo.create_influencer(
            name=name,
            gender=gender,
            licence_number=verified_id if verified_id else None,
            city=city
        )

        # تجهيز بيانات حسابات التواصل
        accounts_data = []
        for platform in ["tiktok", "instagram", "snapchat"]:
            username = request.POST.get(f"{platform}_username")
            if username:
                accounts_data.append({"platform": platform, "username": username})

        self.repo.add_social_accounts(influencer, accounts_data)
        self.repo.add_categories(influencer, categories)

        # messages.success(request, f"")
        return redirect("influencers:thank")

    def list_influencers(self, filters=None, sort_by="id"):
        influencers = self.repo.get_all_influencers()

        if filters:
            if filters.get("search"):
                influencers = influencers.filter(name__icontains=filters["search"])
            if filters.get("city"):
                influencers = influencers.filter(city=filters["city"])
            if filters.get("gender"):
                influencers = influencers.filter(gender=filters["gender"])
            if filters.get("platform"):
                influencers = influencers.filter(social_accounts__platform=filters["platform"])
            if filters.get("followers_min"):
                influencers = influencers.filter(social_accounts__followers_count__gte=filters["followers_min"])
            if filters.get("followers_max"):
                influencers = influencers.filter(social_accounts__followers_count__lte=filters["followers_max"])

        # ترتيب
        if sort_by == "followers_count":
            influencers = influencers.order_by("-social_accounts__followers_count")
        elif sort_by == "engagement_rate":
            influencers = influencers.order_by("-social_accounts__engagement_rate_account")
        else:
            influencers = influencers.order_by("-id")

        return influencers
    

    def get_influencer_detail(self, influencer_id):
        return self.repo.get_influencer_by_id(influencer_id)