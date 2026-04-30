from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel


class AIAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        user = UserModel.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        if not user.is_verified:
            messages.error(request, 'Please verify your email first.')
            return redirect('login')

        return super().dispatch(request, *args, **kwargs)