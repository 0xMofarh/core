from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .services import UserRegistrationService,UserLoginService,PasswordResetService,OTPService
import logging

logger = logging.getLogger(__name__)

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")
    if request.method == "POST":
        data = {
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "remember_me": request.POST.get("remember_me"),
        }

        service = UserLoginService()
        success, message, redirect_url = service.login_user(request, data)
        if success:
            messages.success(request, message)
            return redirect(redirect_url)
        else:
            messages.error(request, message)

    return render(request, "authentication/login.html")


def register_view(request):
    """صفحة التسجيل"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        data = {
            "full_name": request.POST.get('full_name'),
            "email": request.POST.get('email'),
            "mobile_number": request.POST.get('mobile_number'),
            "password": request.POST.get('password'),
            "password_confirm": request.POST.get('password_confirm'),
        }

        service = UserRegistrationService()
        success, message = service.register_user(data)

        if success:
            messages.success(request, message)
            request.session['email_for_otp'] = request.POST.get('email')
            return redirect('authentication:verify_otp')
        else:
            messages.error(request, message)

    return render(request, 'authentication/register.html')



def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        service = PasswordResetService()
        success, message = service.send_reset_code(email)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

    return render(request, 'authentication/reset_password.html')

@login_required
def logout_view(request):
    """تسجيل خروج المستخدم"""
    try:
        if request.user.is_authenticated:
            user_email = request.user.email
            logout(request)
            messages.success(request, "تم تسجيل خروجك بنجاح.")
            logger.info(f"User {user_email} logged out successfully.")
        else:
            messages.info(request, "لم تكن مسجل الدخول.")
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        messages.error(request, "حدث خطأ أثناء تسجيل الخروج.")
    return redirect("authentication:login")




def verify_otp_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        otp_code = request.POST.get("otp_code")

        success, message = OTPService.verify_otp(email, otp_code)
        messages.info(request, message)

        if success:
            return redirect("authentication:login")  # بعد التحقق، يروح لتسجيل الدخول

    return render(request, "authentication/verify_otp.html")








# def email_confirmation_sent_view(request):
#     """صفحة تأكيد إرسال البريد الإلكتروني"""
#     return render(request, 'authentication/email_confirmation_sent.html')

# def email_confirmation_handler_view(request):
#     return render(request, 'authentication/email_confirmation_handler.html')



# def email_confirmation_view(request):
#     if not request.user.is_authenticated:
#         messages.error(request, "يجب تسجيل الدخول أولاً.")
#         return redirect("authentication:login")

#     if not request.user.supabase_user_id:
#         messages.error(request, "لم يتم العثور على بيانات المستخدم.")
#         return redirect("authentication:login")

#     if supabase_auth.is_email_verified(request.user.supabase_user_id):
#         request.user.is_active = True
#         request.user.is_email_verified = True
#         request.user.save()

#         messages.success(request, "تم تفعيل بريدك الإلكتروني بنجاح 🎉")
#         return redirect('dashboard:dashboard')
#         # return redirect("payment:plan")
#     else:
#         messages.warning(request, "البريد الإلكتروني لم يتم تأكيده بعد ⚠️")
#         return redirect("authentication:login")
    


# def reset_password_view(request):
#     """صفحة إعادة تعيين كلمة المرور"""
#     if request.user.is_authenticated:
#         return redirect('dashboard:dashboard')

#     if request.method == 'POST':
#         email = request.POST.get('email')
#         service = PasswordResetService()
#         success, message = service.send_reset_email(email)

#         if success:
#             messages.success(request, message)
#             return redirect('authentication:login')
#         else:
#             messages.error(request, message)

#     return render(request, 'authentication/reset_password.html')
