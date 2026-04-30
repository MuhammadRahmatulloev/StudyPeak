from django.shortcuts import redirect
from django.contrib import messages
from .models import UserModel


def get_current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return UserModel.objects.filter(id=user_id).first()


class SessionLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, 'Please login first!')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')
        user = UserModel.objects.filter(id=user_id).first()
        if not user or not user.is_student:
            messages.error(request, 'Student access required.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class TeacherRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')
        user = UserModel.objects.filter(id=user_id).first()
        if not user or not user.is_teacher:
            messages.error(request, 'Teacher access required.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')
        user = UserModel.objects.filter(id=user_id).first()
        if not user or not user.is_admin_role:
            messages.error(request, 'Admin access required.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class TeacherOrAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')
        user = UserModel.objects.filter(id=user_id).first()
        if not user or (not user.is_teacher and not user.is_admin_role):
            messages.error(request, 'Teacher or admin access required.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)