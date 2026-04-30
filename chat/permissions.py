from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserModel
from .models import Group, GroupMember


def get_current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return UserModel.objects.filter(id=user_id).first()


class GroupMemberRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        group_id = kwargs.get('group_id')
        user = UserModel.objects.filter(id=user_id).first()

        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        is_member = GroupMember.objects.filter(group_id=group_id, user=user).exists()
        if not is_member:
            messages.error(request, 'You are not a member of this group.')
            return redirect('group_list')

        return super().dispatch(request, *args, **kwargs)


class GroupAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        group_id = kwargs.get('group_id')
        user = UserModel.objects.filter(id=user_id).first()

        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        is_admin = GroupMember.objects.filter(group_id=group_id, user=user, role=GroupMember.ADMIN).exists()
        if not is_admin:
            messages.error(request, 'Group admin access required.')
            return redirect('group_detail', group_id=group_id)

        return super().dispatch(request, *args, **kwargs)


class GroupOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login first!')
            return redirect('login')

        group_id = kwargs.get('group_id')
        user = UserModel.objects.filter(id=user_id).first()

        if not user:
            messages.error(request, 'Please login first!')
            return redirect('login')

        is_owner = Group.objects.filter(id=group_id, owner=user).exists()
        if not is_owner:
            messages.error(request, 'Only the group owner can do this.')
            return redirect('group_detail', group_id=group_id)

        return super().dispatch(request, *args, **kwargs)