from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from .repositories import UserRepository, OTPRepository, PasswordResetRepository
import logging
from django.utils import timezone
from datetime import timedelta
import random
import string

logger = logging.getLogger(__name__)

class UserRegistrationService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.otp_repo = OTPRepository()

    def register_user(self, data):
        full_name = data.get("full_name")
        email = data.get("email")
        mobile = data.get("mobile_number")
        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if not all([full_name, email, mobile, password, password_confirm]):
            return False, "يرجى ملء جميع الحقول المطلوبة."

        if password != password_confirm:
            return False, "كلمة المرور غير متطابقة."

        try:
            validate_password(password)
        except ValidationError as e:
            return False, "; ".join(e.messages)

        if self.user_repo.email_exists(email):
            return False, "يوجد حساب بهذا البريد الإلكتروني بالفعل."

        try:
            user = self.user_repo.create_user(
                email=email,
                password=password,
                full_name=full_name,
                mobile_number=mobile
            )

            otp = self.otp_repo.create_otp(user, purpose='registration')
            logger.info(f"OTP created for {user.email}: {otp.code}")
            print(f"OTP created for {user.email}: {otp.code}")

            return True, "تم إنشاء الحساب بنجاح. يرجى التحقق من بريدك الإلكتروني لتفعيل الحساب."

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False, "حدث خطأ في إنشاء الحساب. يرجى المحاولة مرة أخرى."


class UserLoginService:
    def __init__(self):
        self.user_repo = UserRepository()

    def login_user(self, request, data):
        email = data.get("email")
        password = data.get("password")
        remember_me = data.get("remember_me")

        # ✅ التحقق من وجود الحقول
        if not email or not password:
            return False, "يرجى ملء جميع الحقول.", None

        try:
            user = authenticate(request, email=email, password=password)

            if not user:
                return False, "البريد الإلكتروني أو كلمة المرور غير صحيحة.", None

            if not user.is_active:
                return False, "هذا الحساب غير فعّال.", None

            # ✅ تسجيل الدخول
            login(request, user)

            # ✅ إعداد مدة الجلسة
            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 يوم
            else:
                request.session.set_expiry(0)  # تنتهي عند إغلاق المتصفح

            # ✅ تخزين بيانات المستخدم في الجلسة
            request.session["email"] = user.email
            request.session["full_name"] = user.full_name
            request.session["mobile_number"] = user.mobile_number
            request.session["package"] = getattr(user, "package", None)

            # ✅ تحديث آخر تسجيل دخول
            self.user_repo.update_last_login(user)

            return True, "تم تسجيل الدخول بنجاح.", "dashboard:dashboard"

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, "حدث خطأ أثناء تسجيل الدخول. حاول مرة أخرى.", None


class OTPService:
    """مسؤول عن توليد وإرسال والتحقق من أكواد OTP"""

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def send_otp(user_email):
        user = UserRepository().get_user_by_email(user_email)
        if not user:
            return False, "المستخدم غير موجود"

        code = OTPService.generate_code()
        OTPRepository().create_otp(user, purpose='registration', code=code)

        # إرسال الكود عبر البريد
        send_mail(
            subject="رمز التحقق",
            message=f"رمز التحقق الخاص بك هو: {code}\nصالح لمدة 5 دقائق.",
            from_email="no-reply@example.com",
            recipient_list=[user.email]
        )
        return True, "تم إرسال رمز التحقق إلى بريدك الإلكتروني"

    @staticmethod
    def verify_otp(user_email, code):
        user = UserRepository().get_user_by_email(user_email)
        if not user:
            return False, "المستخدم غير موجود"

        otp = OTPRepository().get_valid_otp(user, code)
        if not otp:
            return False, "رمز التحقق غير صحيح"

        if timezone.now() > otp.created_at + timedelta(minutes=5):
            return False, "انتهت صلاحية رمز التحقق"

        OTPRepository().mark_as_verified(otp)
        user.is_email_verified = True
        UserRepository().save(user)
        return True, "تم التحقق من البريد الإلكتروني بنجاح"


class PasswordResetService:
    """مسؤول عن إعادة تعيين كلمة المرور"""

    @staticmethod
    def generate_reset_code(user_email):
        user = UserRepository().get_user_by_email(user_email)
        if not user:
            return False, "المستخدم غير موجود"

        code = OTPService.generate_code()
        PasswordResetRepository().create_reset_code(user, code)

        # إرسال الكود عبر البريد
        send_mail(
            subject="كود إعادة تعيين كلمة المرور",
            message=f"كود إعادة التعيين الخاص بك هو: {code}\nصالح لمدة 5 دقائق.",
            from_email="no-reply@example.com",
            recipient_list=[user.email]
        )
        return True, "تم إرسال كود إعادة التعيين إلى بريدك الإلكتروني"

    @staticmethod
    def verify_reset_code(user_email, code):
        user = UserRepository().get_user_by_email(user_email)
        if not user:
            return False, "المستخدم غير موجود"

        reset_code = PasswordResetRepository().get_valid_code(user, code)
        if not reset_code:
            return False, "الكود غير صحيح"

        if timezone.now() > reset_code.created_at + timedelta(minutes=5):
            return False, "انتهت صلاحية الكود"

        PasswordResetRepository().mark_as_used(reset_code)
        return True, "تم التحقق من الكود بنجاح"
