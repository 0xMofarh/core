from .models import Influencer, SocialAccount,Category
from django.shortcuts import get_object_or_404

class InfluencerRepository:
    def get_all(self):
        return Influencer.objects.all().prefetch_related("social_accounts", "categories")

    def filter_by_name(self, queryset, name):
        if name:
            return queryset.filter(name__icontains=name)
        return queryset

    def filter_by_city(self, queryset, city):
        if city:
            return queryset.filter(city=city)
        return queryset

    def filter_by_gender(self, queryset, gender):
        if gender:
            return queryset.filter(gender=gender)
        return queryset

    def filter_by_platform(self, queryset, platform):
        if platform:
            return queryset.filter(social_accounts__platform=platform)
        return queryset

    def filter_by_followers(self, queryset, min_followers=None, max_followers=None):
        if min_followers:
            queryset = queryset.filter(social_accounts__followers_count__gte=min_followers)
        if max_followers:
            queryset = queryset.filter(social_accounts__followers_count__lte=max_followers)
        return queryset

    def order_by(self, queryset, sort_by):
        if sort_by == "followers_count":
            return queryset.order_by("-socialaccount__followers_count")
        elif sort_by == "engagement_rate":
            return queryset.order_by("-socialaccount__engagement_rate_account")
        else:
            return queryset.order_by("-id")

    def get_cities(self):
        return Influencer.objects.values_list("city", flat=True).distinct()

    def get_platforms(self):
        return SocialAccount.objects.values_list("platform", flat=True).distinct()
    
    def create_influencer(self, name, gender, licence_number, city):
        return Influencer.objects.create(
            name=name,
            gender=gender,
            licence_number=licence_number,
            city=city
        )

    def add_social_accounts(self, influencer, accounts_data):
        accounts = [
            SocialAccount(
                influencer=influencer,
                platform=acc["platform"],
                username=acc["username"]
            )
            for acc in accounts_data
        ]
        SocialAccount.objects.bulk_create(accounts)

    def add_categories(self, influencer, categories):
        for cat in categories:
            category_obj, _ = Category.objects.get_or_create(name=cat)
            influencer.categories.add(category_obj)

    def get_all_influencers(self):
        return Influencer.objects.all().prefetch_related("social_accounts", "categories")
    
    def get_influencer_by_id(self, influencer_id):
        return get_object_or_404(
            Influencer.objects.prefetch_related(
                "categories",
                "social_accounts__account_stats",
                "social_accounts__posts"
            ),
            id=influencer_id
        )
    