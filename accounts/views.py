from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
from .models import UserModel, Profile, Notification


def get_current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return UserModel.objects.filter(id=user_id).first()


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp, username='', subject='StudyPeak — Verification Code'):
    send_mail(
        subject=subject,
        message=(
            f'Hello{" " + username if username else ""}!\n\n'
            f'Your verification code is:\n\n'
            f'        {otp}\n\n'
            f'Enter this 6-digit code on the verification page.\n'
            f'The code is valid for one use only.\n\n'
            f'— StudyPeak Team'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')
        role = request.POST.get('role', UserModel.STUDENT)

        if not all([username, email, password, confirm]):
            messages.error(request, 'Please fill in all fields!')
            return render(request, 'accounts/register.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'accounts/register.html')

        if UserModel.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken!')
            return render(request, 'accounts/register.html')

        if UserModel.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered!')
            return render(request, 'accounts/register.html')

        if role not in [UserModel.STUDENT, UserModel.TEACHER]:
            role = UserModel.STUDENT

        user = UserModel(username=username, email=email, role=role, is_active=False)
        user.set_password(password)
        otp = generate_otp()
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()

        request.session['pending_user_id'] = user.id

        try:
            send_otp_email(email=email, otp=otp, username=username)
        except Exception:
            messages.warning(request, f'Email could not be sent. Your OTP: {otp}')

        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


def verify_otp_view(request):
    pending_id = request.session.get('pending_user_id')
    if not pending_id:
        messages.error(request, 'No pending verification. Please register first.')
        return redirect('register')

    user = UserModel.objects.filter(id=pending_id).first()
    if not user:
        messages.error(request, 'User not found. Please register again.')
        return redirect('register')

    if request.method == 'POST':
        entered = request.POST.get('otp_code', '').strip()
        if entered == user.otp_code:
            user.is_active = True
            user.is_verified = True
            user.otp_code = None
            user.otp_created_at = None
            user.save()
            del request.session['pending_user_id']
            messages.success(request, 'Email verified! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'accounts/verify_otp.html', {'email': user.email})


def login_view(request):
    if request.method != 'POST':
        return render(request, 'accounts/login.html')

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    user = UserModel.objects.filter(username=username).first()

    if not user or not user.check_password(password):
        messages.error(request, 'Invalid username or password!')
        return render(request, 'accounts/login.html')

    if not user.is_active:
        messages.error(request, 'Your account is not active. Please verify your email.')
        return render(request, 'accounts/login.html')

    if not user.is_verified:
        request.session['pending_user_id'] = user.id
        otp = generate_otp()
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()
        try:
            send_otp_email(email=user.email, otp=otp, username=user.username)
        except Exception:
            messages.warning(request, f'Email could not be sent. Your OTP: {otp}')
        return redirect('verify_otp')

    request.session['user_id'] = user.id
    messages.success(request, f'Welcome back, {user.username}!')
    return redirect('home')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = UserModel.objects.filter(email=email).first()

        if user:
            otp = generate_otp()
            user.otp_code = otp
            user.otp_created_at = timezone.now()
            user.save()
            request.session['reset_email'] = email
            try:
                send_otp_email(
                    email=email,
                    otp=otp,
                    username=user.username,
                    subject='StudyPeak — Password Reset Code'
                )
            except Exception:
                messages.warning(request, f'Email not sent. Your reset code: {otp}')

        messages.success(request, 'If this email exists — a reset code has been sent!')
        return redirect('reset_verify_otp')

    return render(request, 'accounts/reset_request.html')


def reset_verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please request a reset again.')
        return redirect('reset_request')

    user = UserModel.objects.filter(email=email).first()
    if not user:
        messages.error(request, 'User not found.')
        return redirect('reset_request')

    if request.method == 'POST':
        entered = request.POST.get('otp_code', '').strip()
        if entered == user.otp_code:
            user.otp_code = None
            user.otp_created_at = None
            user.save()
            request.session['reset_verified_id'] = user.id
            del request.session['reset_email']
            return redirect('reset_new_password')
        else:
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'accounts/reset_verify_otp.html', {'email': email})


def reset_new_password_view(request):
    verified_id = request.session.get('reset_verified_id')
    if not verified_id:
        messages.error(request, 'Session expired. Please request a reset again.')
        return redirect('reset_request')

    user = UserModel.objects.filter(id=verified_id).first()
    if not user:
        return redirect('reset_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if new_password != confirm:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'accounts/reset_confirm.html')

        user.set_password(new_password)
        user.save()
        del request.session['reset_verified_id']
        messages.success(request, 'Password changed successfully! Please log in.')
        return redirect('login')

    return render(request, 'accounts/reset_confirm.html')


class ProfileView(View):
    def get(self, request):
        user = get_current_user(request)
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        profile = Profile.objects.filter(user=user).first()
        notifications = Notification.objects.filter(user=user).order_by('-created_at')[:20]

        return render(request, 'accounts/profile.html', {
            'user': user,
            'profile': profile,
            'notifications': notifications,
        })


class ProfileUpdateView(View):
    def get(self, request):
        user = get_current_user(request)
        if not user:
            return redirect('login')
        profile = Profile.objects.filter(user=user).first()
        return render(request, 'accounts/profile_update.html', {
            'user': user,
            'profile': profile,
        })

    def post(self, request):
        user = get_current_user(request)
        if not user:
            return redirect('login')

        profile = Profile.objects.filter(user=user).first()

        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.save()

        profile.bio = request.POST.get('bio', profile.bio)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.status = request.POST.get('status', profile.status)
        profile.post_text = request.POST.get('post_text', profile.post_text)

        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')


class ChangePasswordView(View):
    def get(self, request):
        user = get_current_user(request)
        if not user:
            return redirect('login')
        return render(request, 'accounts/change_password.html')

    def post(self, request):
        user = get_current_user(request)
        if not user:
            return redirect('login')

        old = request.POST.get('old_password', '')
        new = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if not user.check_password(old):
            messages.error(request, 'Old password is incorrect!')
            return render(request, 'accounts/change_password.html')

        if new != confirm:
            messages.error(request, 'New passwords do not match!')
            return render(request, 'accounts/change_password.html')

        user.set_password(new)
        user.save()
        request.session.flush()
        messages.success(request, 'Password updated! Please log in again.')
        return redirect('login')