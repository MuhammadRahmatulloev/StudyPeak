from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel


class DashboardAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')
        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class StudentProgressAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')
        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')
        student_id = kwargs.get('student_id') or request.GET.get('student_id')
        if student_id and user.is_student:
            if str(user.id) != str(student_id):
                messages.error(request, 'You can only view your own progress.')
                return redirect('student_progress')
        return super().dispatch(request, *args, **kwargs)