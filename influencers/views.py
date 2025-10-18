from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from django.core.paginator import Paginator
from .models import Influencer, SocialAccount, Category,Post,AccountStat


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import InfluencerService

@login_required
def influencers_search(request):
    # جمع الفلاتر من GET
    filters = {
        "search": request.GET.get("search", ""),
        "city": request.GET.get("city", ""),
        "gender": request.GET.get("gender", ""),
        "platform": request.GET.get("platform", ""),
        "followers_min": request.GET.get("followers_min"),
        "followers_max": request.GET.get("followers_max"),
        "sort_by": request.GET.get("sort_by", "id"),
    }
    page_number = request.GET.get("page", 1)

    # استدعاء الـ service
    service = InfluencerService()
    data = service.search_influencers(filters, page_number)

    return render(request, "influencers/influencers_search.html", data)

@login_required
def add_influencer(request):
    if request.method == "POST":
        service = InfluencerService()
        return service.add_influencer(request)

    return render(request, "influencers/influencer_form.html")

# @login_required
# def influencers_search(request):
#     search_query = request.GET.get("search", "")
#     city = request.GET.get("city", "")
#     gender = request.GET.get("gender", "")
#     platform = request.GET.get("platform", "")
#     followers_min = request.GET.get("followers_min")
#     followers_max = request.GET.get("followers_max")
#     sort_by = request.GET.get("sort_by", "id")

#     influencers = Influencer.objects.all().prefetch_related("social_accounts", "categories")

#     # البحث
#     if search_query:
#         influencers = influencers.filter(name__icontains=search_query)

#     # الفلاتر
#     if city:
#         influencers = influencers.filter(city=city)
#     if gender:
#         influencers = influencers.filter(gender=gender)
#     if followers_min:
#         influencers = influencers.filter(socialaccount__followers_count__gte=followers_min)
#     if followers_max:
#         influencers = influencers.filter(socialaccount__followers_count__lte=followers_max)
#     if platform:
#         influencers = influencers.filter(socialaccount__platform=platform)

#     # ترتيب
#     if sort_by == "followers_count":
#         influencers = influencers.order_by("-socialaccount__followers_count")
#     elif sort_by == "engagement_rate":
#         influencers = influencers.order_by("-socialaccount__engagement_rate_account")
#     else:
#         influencers = influencers.order_by("-id")

#     # تجهيز البيانات النهائية مع الإحصائيات
#     influencers_data = []
#     for inf in influencers:
#         accounts = SocialAccount.objects.filter(influencer=inf)
#         accounts_data = [
#             {
#                 "platform": acc.platform,
#                 "username": acc.username,
#                 "followers_count": acc.followers_count,
#                 "engagement_rate_account": acc.engagement_rate_account,
#                 "is_verified": acc.is_verified,
#             }
#             for acc in accounts
#         ]

#         # إجمالي المتابعين من كل الحسابات
#         total_followers = sum(acc.followers_count for acc in accounts)

#         influencers_data.append({
#             "id": inf.id,
#             "name": inf.name,
#             "city": inf.city,
#             "gender": inf.gender,
#             "avatar": inf.avatar,
#             "social_accounts": accounts_data,
#             "total_followers": total_followers,
#             "created_at": inf.created_at,
#         })

#     # التصفح (pagination)
#     paginator = Paginator(influencers_data, 9)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     cities = Influencer.objects.values_list("city", flat=True).distinct()
#     platforms = SocialAccount.objects.values_list("platform", flat=True).distinct()

#     context = {
#         "page_obj": page_obj,
#         "filters": {
#             "search": search_query,
#             "city": city,
#             "gender": gender,
#             "platform": platform,
#             "followers_min": followers_min,
#             "followers_max": followers_max,
#             "sort_by": sort_by,
#         },
#         "cities": cities,
#         "platforms": platforms,
#     }

#     return render(request, "influencers/influencers_search.html", context)

def add_influencer(request):
    if request.method == "POST":
        name = request.POST.get("name")
        gender = request.POST.get("gender")
        verified_id = request.POST.get("verified_id")
        contact_phone = request.POST.get("contact_phone")
        city = request.POST.get("city")
        categories = request.POST.getlist("categories")

        # إنشاء المؤثر
        influencer = Influencer.objects.create(
            name=name,
            gender=gender,
            licence_number=verified_id if verified_id else None,
            city=city,
        )

        # إضافة حسابات التواصل الاجتماعي
        tiktok_username = request.POST.get("tiktok_username")
        instagram_username = request.POST.get("instagram_username")
        snapchat_username = request.POST.get("snapchat_username")

        social_accounts = []
        if tiktok_username:
            social_accounts.append(SocialAccount(
                influencer=influencer,
                platform="tiktok",
                username=tiktok_username
                
            ))
        if instagram_username:
            social_accounts.append(SocialAccount(
                influencer=influencer,
                platform="instagram",
                username=instagram_username
                
            ))
        if snapchat_username:
            social_accounts.append(SocialAccount(
                influencer=influencer,
                platform="snapchat",
                username=snapchat_username,
            ))

        # حفظ جميع الحسابات دفعة واحدة
        SocialAccount.objects.bulk_create(social_accounts)

        # ربط التصنيفات
        for cat in categories:
            category_obj, created = Category.objects.get_or_create(name=cat)
            influencer.categories.add(category_obj)

        messages.success(request, f"تمت إضافة المؤثر {name} بنجاح ✅")
        return redirect("influencers:thank")  # غير هذا باسم المسار الذي تريد تحويل المستخدم له بعد الإضافة

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
