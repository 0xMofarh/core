# from django.shortcuts import redirect
# from django.contrib import messages
# from functools import wraps
# # from services.supabase_auth import supabase_auth
# import logging

# logger = logging.getLogger(__name__)

# def subscription_required(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         supabase_user_id = request.session.get("supabase_user_id")
#         # if not supabase_user_id:
#         #     messages.error(request, "يرجى تسجيل الدخول أولاً.")
#         #     return redirect("authentication:login")
#         try:
#             # تحقق إذا عند المستخدم باقة نشطة
#             result = supabase_auth.client.from_("subscriptions")\
#                 .select("*")\
#                 .eq("user_id", supabase_user_id)\
#                 .eq("status", "active")\
#                 .execute()
#             print(result)
#             if result.error:
#                 logger.error(f"خطأ فحص الاشتراك: {result.error}")
#                 messages.error(request, "حدث خطأ أثناء التحقق من الاشتراك.")
#                 return redirect("payment:plan")

#             if not result.data or len(result.data) == 0:
#                 messages.info(request, "لم يتم العثور على باقة نشطة. اختر باقة الآن.")
#                 return redirect("payment:plan")

#         except Exception as e:
#             logger.error(f"خطأ في subscription_required: {str(e)}")
#             messages.error(request, "حدث خطأ أثناء التحقق من الاشتراك.")
#             return redirect("payment:plan")

#         return view_func(request, *args, **kwargs)

#     return wrapper
