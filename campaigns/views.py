from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Campaign
from .services import CampaignService,CampaignParticipantService



service = CampaignService()

@login_required
def campaigns_list(request):
    """عرض قائمة الحملات"""
    filters = {
        'status': request.GET.get('status')
    }
    page_number = request.GET.get('page')
    context = service.list_campaigns(request.user, filters, page_number)
    context.update({
        'status_choices': Campaign.STATUS_CHOICES,
        'filters': filters
    })
    return render(request, 'campaigns/campaigns_list.html', context)


@login_required
def campaign_detail(request, campaign_id):
    """صفحة تفاصيل الحملة"""
    context = service.get_campaign_details(request.user, campaign_id)
    return render(request, 'campaigns/campaign_detail.html', context)


@login_required
def create_campaign(request):
    """إنشاء حملة جديدة"""
    if request.method == 'POST':
        response = service.create_campaign(request)
        if response:
            return response  # redirect بعد الإنشاء

    context = {'campaign_types': service.repo.get_campaign_model().CAMPAIGN_TYPE_CHOICES}
    return render(request, 'campaigns/create_campaign.html', context)


@login_required
def edit_campaign(request, campaign_id):
    """تعديل حملة موجودة"""
    campaign = service.repo.get_user_campaign_by_id(campaign_id, request.user)

    if request.method == 'POST':
        response = service.edit_campaign(request, campaign_id)
        if response:
            return response  # redirect بعد التعديل

    context = {
        'campaign': campaign,
        'campaign_types': campaign.CAMPAIGN_TYPE_CHOICES,
        'status_choices': campaign.STATUS_CHOICES,
    }
    return render(request, 'campaigns/edit_campaign.html', context)

@login_required
def delete_campaign(request, campaign_id):
    """
    حذف حملة (يُنفذ فقط عبر POST)
    """
    service = CampaignService()

    if request.method == "POST":
        try:
            service.delete_campaign(campaign_id, request.user)
            messages.success(request, "تم حذف الحملة بنجاح ✅")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حذف الحملة: {str(e)}")
    else:
        messages.warning(request, "طريقة غير صالحة للحذف.")

    return redirect('campaigns:campaigns_list')

@login_required
def add_participant(request, campaign_id):
    service = CampaignParticipantService()

    if request.method == 'POST':
        try:
            campaign = service.add_participant(request, campaign_id)
            return redirect('campaigns:campaign_detail', campaign_id=campaign.id)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إضافة المؤثر: {str(e)}')

    campaign = service.campaign_repo.get_campaign_by_id(campaign_id, request.user)
    available_influencers = service.get_available_influencers()

    context = {
        'campaign': campaign,
        'available_influencers': available_influencers,
    }

    return render(request, 'campaigns/add_participant.html', context)

# @login_required
# def update_participant_status(request, participant_id):
#     """
#     تحديث حالة مشارك في الحملة
#     """
#     if request.method == 'POST':
#         try:
#             participant = get_object_or_404(CampaignParticipant, id=participant_id)
            
#             # التأكد من أن المستخدم هو منشئ الحملة
#             if participant.campaign.created_by != request.user:
#                 return JsonResponse({'success': False, 'message': 'غير مصرح لك بتعديل هذه الحملة'})
            
#             new_status = request.POST.get('status')
#             participant.status = new_status
#             participant.is_accepted = (new_status == 'accepted')
            
#             if new_status == 'accepted':
#                 participant.accepted_at = timezone.now()
#             elif new_status == 'completed':
#                 participant.completed_at = timezone.now()
            
#             participant.save()
            
#             return JsonResponse({
#                 'success': True,
#                 'message': f'تم تحديث حالة {participant.influencer.name} إلى {participant.get_status_display()}'
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'message': f'حدث خطأ أثناء تحديث الحالة: {str(e)}'
#             })
    
#     return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

@login_required
@require_POST
def add_participant_api(request, campaign_id):
    try:
        data = json.loads(request.body)
        influencer_id = data.get('influencer_id')

        if not influencer_id:
            return JsonResponse({'success': False, 'error': 'لم يتم إرسال معرف المؤثر'}, status=400)

        service = CampaignParticipantService()

        campaign = service.campaign_repo.get_campaign_by_id(campaign_id, request.user)
        influencer = service.influencer_repo.get_influencer_by_id(influencer_id)
        participant, created = service.participant_repo.add_participant(
            campaign, influencer, None, None
        )

        if created:
            return JsonResponse({
                'success': True,
                'message': f'تم إضافة {influencer.name} إلى الحملة {campaign.title} بنجاح!',
                'campaign_id': campaign.id,
                'influencer_id': influencer.id,
                'influencer_name': influencer.name,
                'influencer_active': getattr(influencer, "is_active", True),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'{influencer.name} موجود بالفعل في هذه الحملة'
            })
    except Exception as e:
        import traceback
        print("❌ Error in add_participant_api:", e)
        traceback.print_exc()  # هذا يطبع الخطأ الكامل في الطرفية
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def campaigns_list_api(request):
    service = CampaignService()
    campaigns_data = service.repo.get_user_campaigns(request.user)
    
    campaigns = [
        {
            'id': c.id,
            'title': c.title,
            'description': c.description or '',
        } for c in campaigns_data
    ]
    return JsonResponse({'success': True, 'campaigns': campaigns})



@login_required
def remove_participant_view(request, campaign_id, influencer_id):
    service = CampaignParticipantService()
    
    if request.method == "POST":
        service.remove_participant(request, campaign_id, influencer_id)
    
    return redirect('campaigns:campaign_detail', campaign_id=campaign_id)

@login_required
def accept_participant_view(request, campaign_id, influencer_id):
    service = CampaignParticipantService()

    if request.method == "POST":
        service.accept_participant(request, campaign_id, influencer_id)

    return redirect('campaigns:campaign_detail', campaign_id=campaign_id)
# @login_required
# @csrf_exempt
# @require_http_methods(["POST"])
# def remove_participant_from_campaign(request, participant_id):
#     """
#     حذف مؤثر من حملة
#     """
#     try:
#         # الحصول على مشارك الحملة
#         participant = get_object_or_404(CampaignParticipant, id=participant_id)
        
#         # التحقق من أن المستخدم يملك الحملة
#         if participant.campaign.created_by != request.user:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'ليس لديك صلاحية لحذف هذا المؤثر'
#             })
        
#         influencer_name = participant.influencer.name
#         campaign_title = participant.campaign.title
        
#         # حذف المشارك
#         participant.delete()
        
#         print(f"DEBUG: Successfully removed participant {participant_id}")
        
#         return JsonResponse({
#             'success': True,
#             'message': f'تم حذف المؤثر "{influencer_name}" من الحملة "{campaign_title}" بنجاح',
#             'influencer_name': influencer_name,
#             'campaign_title': campaign_title
#         })
        
#     except Exception as e:
#         print(f"DEBUG: Error removing participant: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({
#             'success': False,
#             'error': f'حدث خطأ أثناء الحذف: {str(e)}'
#         })


# @login_required
# @csrf_exempt
# @require_http_methods(["POST"])
# def add_participant_to_campaign(request, campaign_id):
#     """
#     إضافة ID مؤثر إلى حملة
#     """
#     print(f"DEBUG: add_participant_to_campaign called with campaign_id={campaign_id}")
#     print(f"DEBUG: User: {request.user}")
#     print(f"DEBUG: Request method: {request.method}")
#     print(f"DEBUG: Request body: {request.body}")
    
#     try:
#         campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)
#         print(f"DEBUG: Campaign found: {campaign.title}")
        
#         # قراءة البيانات من JSON
#         data = json.loads(request.body)
#         influencer_id = data.get('influencer_id')
#         print(f"DEBUG: Parsed data: {data}")
#         print(f"DEBUG: Influencer ID: {influencer_id}")
        
#         if not influencer_id:
#             print("DEBUG: No influencer_id provided")
#             return JsonResponse({
#                 'success': False,
#                 'error': 'معرف المؤثر مطلوب'
#             })
        
#         # التحقق من وجود المؤثر في قاعدة البيانات (بدون التحقق من is_active)
#         try:
#             influencer = Influencer.objects.get(id=influencer_id)
#             print(f"DEBUG: Influencer found: {influencer.name} (is_active: {influencer.is_active})")
#         except Influencer.DoesNotExist:
#             print(f"DEBUG: Influencer {influencer_id} not found")
#             return JsonResponse({
#                 'success': False,
#                 'error': 'المؤثر غير موجود في قاعدة البيانات'
#             })
        
#         # إنشاء مشاركة بسيطة لإضافة ID المؤثر للحملة
#         participant, created = CampaignParticipant.objects.get_or_create(
#             campaign=campaign,
#             influencer=influencer,
#             defaults={
#                 'status': 'pending',
#                 'is_accepted': False,
#                 'proposed_price': 0.00,
#                 'deliverables': 'سيتم تحديد التسليمات لاحقاً'
#             }
#         )
        
#         print(f"DEBUG: Participant created: {created}")
#         print(f"DEBUG: Participant ID: {participant.id}")
        
#         if not created:
#             print("DEBUG: Participant already exists")
#             return JsonResponse({
#                 'success': False,
#                 'error': 'المؤثر موجود بالفعل في هذه الحملة'
#             })
        
#         print("DEBUG: Successfully created participant")
#         return JsonResponse({
#             'success': True,
#             'message': f'تم إضافة المؤثر "{influencer.name}" (ID: {influencer_id}) إلى الحملة بنجاح',
#             'influencer_id': influencer_id,
#             'influencer_name': influencer.name,
#             'campaign_id': campaign_id,
#             'influencer_active': influencer.is_active
#         })
        
#     except json.JSONDecodeError as e:
#         print(f"DEBUG: JSON decode error: {e}")
#         return JsonResponse({
#             'success': False,
#             'error': 'بيانات غير صالحة'
#         })
#     except Exception as e:
#         print(f"DEBUG: General error: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({
#             'success': False,
#             'error': f'حدث خطأ: {str(e)}'
#         })