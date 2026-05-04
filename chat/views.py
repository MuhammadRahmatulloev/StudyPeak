from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from accounts.models import UserModel, Profile
from accounts.permissions import SessionLoginRequiredMixin, get_current_user
from .models import Friendship, Conversation, Group, GroupMember, GroupInvitation, Message
import json
from django.http import JsonResponse


def get_chat_sidebar(user):
    sidebar_groups = []
    for g in Group.objects.filter(memberships__user=user).order_by('-created_at'):
        last_msg = g.messages.filter(is_deleted=False).order_by('created_at').last()
        sidebar_groups.append({'group': g, 'last_msg': last_msg})

    sidebar_convs = []
    for conv in user.conversations.all().order_by('-created_at'):
        other = conv.participants.exclude(id=user.id).first()
        if other:
            last_msg = conv.messages.filter(is_deleted=False).order_by('created_at').last()
            sidebar_convs.append({'conv': conv, 'other': other, 'last_msg': last_msg})

    return sidebar_groups, sidebar_convs


class ChatHomeView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        first_group = Group.objects.filter(memberships__user=user).order_by('-created_at').first()
        if first_group:
            return redirect('group_detail', group_id=first_group.id)
        first_conv = user.conversations.order_by('-created_at').first()
        if first_conv:
            return redirect('conversation_detail', conversation_id=first_conv.id)
        return redirect('group_create')


class SearchUsersView(SessionLoginRequiredMixin, View):
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        q = request.GET.get('q', '').strip()
        
        if len(q) < 2:
            return JsonResponse({'users': []})
        
        existing_ids = group.memberships.values_list('user_id', flat=True)
        users = UserModel.objects.filter(
            username__icontains=q
        ).exclude(id__in=existing_ids)[:8]
        
        data = [{'id': u.id, 'username': u.username, 'role': u.role} for u in users]
        return JsonResponse({'users': data})


class EditMessageView(SessionLoginRequiredMixin, View):
    def post(self, request, message_id):
        user = get_current_user(request)
        message = get_object_or_404(Message, id=message_id, sender=user)
        content = request.POST.get('content', '').strip()
        if content:
            message.content = content
            message.save()
        if message.group:
            return redirect('group_detail', group_id=message.group.id)
        return redirect('conversation_detail', conversation_id=message.conversation.id)
    

class FriendListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        friendships = Friendship.objects.filter(
            status=Friendship.ACCEPTED
        ).filter(
            sender=user
        ) | Friendship.objects.filter(
            status=Friendship.ACCEPTED
        ).filter(
            receiver=user
        )

        friends = []
        for f in friendships:
            friend = f.receiver if f.sender == user else f.sender
            friends.append(friend)

        pending_received = Friendship.objects.filter(receiver=user, status=Friendship.PENDING)
        pending_sent = Friendship.objects.filter(sender=user, status=Friendship.PENDING)

        return render(request, 'chat/friend_list.html', {
            'friends': friends,
            'pending_received': pending_received,
            'pending_sent': pending_sent,
        })


class SendFriendRequestView(SessionLoginRequiredMixin, View):
    def post(self, request, user_id):
        user = get_current_user(request)
        target = get_object_or_404(UserModel, id=user_id)

        if target == user:
            messages.error(request, 'You cannot send a friend request to yourself.')
            return redirect('friend_list')

        exists = Friendship.objects.filter(
            sender=user, receiver=target
        ).exists() or Friendship.objects.filter(
            sender=target, receiver=user
        ).exists()

        if exists:
            messages.warning(request, 'Friend request already exists.')
            return redirect('friend_list')

        Friendship.objects.create(sender=user, receiver=target)
        messages.success(request, f'Friend request sent to {target.username}.')
        return redirect('friend_list')


class AcceptFriendRequestView(SessionLoginRequiredMixin, View):
    def post(self, request, friendship_id):
        user = get_current_user(request)
        friendship = get_object_or_404(Friendship, id=friendship_id, receiver=user)
        friendship.status = Friendship.ACCEPTED
        friendship.save()
        messages.success(request, f'You are now friends with {friendship.sender.username}.')
        return redirect('friend_list')


class RejectFriendRequestView(SessionLoginRequiredMixin, View):
    def post(self, request, friendship_id):
        user = get_current_user(request)
        friendship = get_object_or_404(Friendship, id=friendship_id, receiver=user)
        friendship.status = Friendship.REJECTED
        friendship.save()
        messages.info(request, 'Friend request rejected.')
        return redirect('friend_list')


class RemoveFriendView(SessionLoginRequiredMixin, View):
    def post(self, request, user_id):
        user = get_current_user(request)
        target = get_object_or_404(UserModel, id=user_id)

        friendship = Friendship.objects.filter(
            sender=user, receiver=target, status=Friendship.ACCEPTED
        ).first() or Friendship.objects.filter(
            sender=target, receiver=user, status=Friendship.ACCEPTED
        ).first()

        if friendship:
            friendship.delete()
            messages.success(request, f'{target.username} removed from friends.')
        else:
            messages.error(request, 'Friendship not found.')

        return redirect('friend_list')


class ConversationListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        conversations = user.conversations.all().order_by('-created_at')
        return render(request, 'chat/conversation_list.html', {
            'conversations': conversations,
        })


class ConversationDetailView(SessionLoginRequiredMixin, View):
    def get(self, request, conversation_id):
        user = get_current_user(request)
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)
        other_user = conversation.participants.exclude(id=user.id).first()
        messages_qs = conversation.messages.filter(is_deleted=False).order_by('created_at')
        sidebar_groups, sidebar_convs = get_chat_sidebar(user)

        friendship = None
        is_friend = False
        if other_user:
            friendship = Friendship.objects.filter(
                sender=user, receiver=other_user, status=Friendship.ACCEPTED
            ).first() or Friendship.objects.filter(
                sender=other_user, receiver=user, status=Friendship.ACCEPTED
            ).first()
            is_friend = bool(friendship)

        return render(request, 'chat/conversation_detail.html', {
            'conversation': conversation,
            'messages': messages_qs,
            'other_user': other_user,
            'is_friend': is_friend,
            'friendship': friendship,
            'sidebar_groups': sidebar_groups,
            'sidebar_convs': sidebar_convs,
            'user': user,
        })

    def post(self, request, conversation_id):
        user = get_current_user(request)
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)
        content = request.POST.get('content', '').strip()
        if not content:
            messages.error(request, 'Message cannot be empty.')
            return redirect('conversation_detail', conversation_id=conversation_id)
        Message.objects.create(conversation=conversation, sender=user, content=content)
        return redirect('conversation_detail', conversation_id=conversation_id)


class StartConversationView(SessionLoginRequiredMixin, View):
    def get(self, request, user_id):
        return self.post(request, user_id)

    def post(self, request, user_id):
        user = get_current_user(request)
        target = get_object_or_404(UserModel, id=user_id)

        if target == user:
            messages.error(request, 'You cannot start a conversation with yourself.')
            return redirect('conversation_list')

        for conv in user.conversations.all():
            if conv.participants.count() == 2 and conv.participants.filter(id=target.id).exists():
                return redirect('conversation_detail', conversation_id=conv.id)

        conversation = Conversation.objects.create()
        conversation.participants.add(user, target)
        return redirect('conversation_detail', conversation_id=conversation.id)


class GroupListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        groups = Group.objects.filter(memberships__user=user)
        return render(request, 'chat/group_list.html', {
            'groups': groups,
        })


class GroupCreateView(SessionLoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'chat/group_create.html')

    def post(self, request):
        user = get_current_user(request)
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_study_group = request.POST.get('is_study_group') == 'on'

        if not name:
            messages.error(request, 'Group name is required.')
            return render(request, 'chat/group_create.html')

        group = Group.objects.create(
            name=name,
            description=description,
            owner=user,
            is_study_group=is_study_group,
        )

        if request.FILES.get('avatar'):
            group.avatar = request.FILES['avatar']
            group.save()

        GroupMember.objects.create(group=group, user=user, role=GroupMember.ADMIN)
        messages.success(request, f'Group "{group.name}" created.')
        return redirect('group_detail', group_id=group.id)


class GroupDetailView(SessionLoginRequiredMixin, View):
    def get(self, request, group_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id)
        membership = GroupMember.objects.filter(group=group, user=user).first()
        if not membership:
            messages.error(request, 'You are not a member of this group.')
            return redirect('group_list')

        messages_qs = group.messages.filter(is_deleted=False).order_by('created_at')
        pinned = group.messages.filter(is_pinned=True, is_deleted=False)
        members = group.memberships.select_related('user', 'user__profile').all()
        sidebar_groups, sidebar_convs = get_chat_sidebar(user)
        linked_subject = group.subjects.first()

        return render(request, 'chat/group_detail.html', {
            'group': group,
            'messages': messages_qs,
            'pinned': pinned,
            'members': members,
            'membership': membership,
            'sidebar_groups': sidebar_groups,
            'sidebar_convs': sidebar_convs,
            'linked_subject': linked_subject,
            'user': user,
        })

    def post(self, request, group_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id)
        membership = GroupMember.objects.filter(group=group, user=user).first()
        if not membership:
            messages.error(request, 'You are not a member of this group.')
            return redirect('group_list')
        content = request.POST.get('content', '').strip()
        if not content:
            messages.error(request, 'Message cannot be empty.')
            return redirect('group_detail', group_id=group_id)
        Message.objects.create(group=group, sender=user, content=content)
        return redirect('group_detail', group_id=group_id)


class GroupUpdateView(SessionLoginRequiredMixin, View):
    def get(self, request, group_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id)

        membership = GroupMember.objects.filter(group=group, user=user, role=GroupMember.ADMIN).first()
        if not membership:
            messages.error(request, 'Admin access required.')
            return redirect('group_detail', group_id=group_id)

        return render(request, 'chat/group_update.html', {'group': group})

    def post(self, request, group_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id)

        membership = GroupMember.objects.filter(group=group, user=user, role=GroupMember.ADMIN).first()
        if not membership:
            messages.error(request, 'Admin access required.')
            return redirect('group_detail', group_id=group_id)

        group.name = request.POST.get('name', group.name).strip()
        group.description = request.POST.get('description', group.description)
        group.is_study_group = request.POST.get('is_study_group') == 'on'

        if request.FILES.get('avatar'):
            group.avatar = request.FILES['avatar']

        group.save()
        messages.success(request, 'Group updated successfully.')
        return redirect('group_detail', group_id=group_id)


class GroupDeleteView(SessionLoginRequiredMixin, View):
    def post(self, request, group_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id, owner=user)
        group.delete()
        messages.success(request, 'Group deleted.')
        return redirect('group_list')


class GroupLeaveView(SessionLoginRequiredMixin, View):
    def post(self, request, group_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id)

        if group.owner == user:
            messages.error(request, 'Owner cannot leave the group. Transfer ownership or delete the group.')
            return redirect('group_detail', group_id=group_id)

        GroupMember.objects.filter(group=group, user=user).delete()
        messages.success(request, f'You left "{group.name}".')
        return redirect('group_list')


class GroupKickMemberView(SessionLoginRequiredMixin, View):
    def post(self, request, group_id, user_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id)

        membership = GroupMember.objects.filter(group=group, user=user, role=GroupMember.ADMIN).first()
        if not membership:
            messages.error(request, 'Admin access required.')
            return redirect('group_detail', group_id=group_id)

        target = get_object_or_404(UserModel, id=user_id)

        if target == group.owner:
            messages.error(request, 'Cannot kick the group owner.')
            return redirect('group_detail', group_id=group_id)

        GroupMember.objects.filter(group=group, user=target).delete()
        messages.success(request, f'{target.username} removed from the group.')
        return redirect('group_detail', group_id=group_id)


class GroupChangeMemberRoleView(SessionLoginRequiredMixin, View):
    def post(self, request, group_id, user_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id, owner=user)
        target = get_object_or_404(UserModel, id=user_id)

        member = GroupMember.objects.filter(group=group, user=target).first()
        if not member:
            messages.error(request, 'User is not a member of this group.')
            return redirect('group_detail', group_id=group_id)

        new_role = request.POST.get('role')
        if new_role not in [GroupMember.ADMIN, GroupMember.MEMBER]:
            messages.error(request, 'Invalid role.')
            return redirect('group_detail', group_id=group_id)

        member.role = new_role
        member.save()
        messages.success(request, f'{target.username} role updated to {new_role}.')
        return redirect('group_detail', group_id=group_id)

class SendGroupInvitationView(SessionLoginRequiredMixin, View):
    def post(self, request, group_id):
        user = get_current_user(request)
        group = get_object_or_404(Group, id=group_id)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        membership = GroupMember.objects.filter(group=group, user=user, role=GroupMember.ADMIN).first()
        if not membership:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Admin access required.'})
            messages.error(request, 'Admin access required.')
            return redirect('group_detail', group_id=group_id)

        receiver_id = request.POST.get('user_id')
        receiver = get_object_or_404(UserModel, id=receiver_id)

        if GroupMember.objects.filter(group=group, user=receiver).exists():
            if is_ajax:
                return JsonResponse({'status': 'already', 'message': f'{receiver.username} is already a member.'})
            messages.warning(request, f'{receiver.username} is already a member.')
            return redirect('group_detail', group_id=group_id)

        if GroupInvitation.objects.filter(group=group, receiver=receiver, status=GroupInvitation.PENDING).exists():
            if is_ajax:
                return JsonResponse({'status': 'already', 'message': f'Invitation already sent to {receiver.username}.'})
            messages.warning(request, f'Invitation already sent to {receiver.username}.')
            return redirect('group_detail', group_id=group_id)

        GroupInvitation.objects.create(group=group, sender=user, receiver=receiver)

        if is_ajax:
            return JsonResponse({'status': 'ok', 'message': f'Invitation sent to {receiver.username}!'})
        messages.success(request, f'Invitation sent to {receiver.username}.')
        return redirect('group_detail', group_id=group_id)


class AcceptGroupInvitationView(SessionLoginRequiredMixin, View):
    def post(self, request, invitation_id):
        user = get_current_user(request)
        invitation = get_object_or_404(GroupInvitation, id=invitation_id, receiver=user, status=GroupInvitation.PENDING)

        GroupMember.objects.get_or_create(group=invitation.group, user=user, defaults={'role': GroupMember.MEMBER})
        invitation.status = GroupInvitation.ACCEPTED
        invitation.save()

        messages.success(request, f'You joined "{invitation.group.name}".')
        return redirect('group_detail', group_id=invitation.group.id)


class RejectGroupInvitationView(SessionLoginRequiredMixin, View):
    def post(self, request, invitation_id):
        user = get_current_user(request)
        invitation = get_object_or_404(GroupInvitation, id=invitation_id, receiver=user, status=GroupInvitation.PENDING)
        invitation.status = GroupInvitation.REJECTED
        invitation.save()
        messages.info(request, 'Group invitation rejected.')
        return redirect('group_list')


class PinMessageView(SessionLoginRequiredMixin, View):
    def post(self, request, message_id):
        user = get_current_user(request)
        message = get_object_or_404(Message, id=message_id)

        if message.group:
            membership = GroupMember.objects.filter(group=message.group, user=user, role=GroupMember.ADMIN).first()
            if not membership:
                messages.error(request, 'Admin access required.')
                return redirect('group_detail', group_id=message.group.id)
            message.is_pinned = not message.is_pinned
            message.save()
            return redirect('group_detail', group_id=message.group.id)

        messages.error(request, 'Cannot pin this message.')
        return redirect('group_list')


class DeleteMessageView(SessionLoginRequiredMixin, View):
    def post(self, request, message_id):
        user = get_current_user(request)
        message = get_object_or_404(Message, id=message_id)

        if message.group:
            membership = GroupMember.objects.filter(group=message.group, user=user).first()
            if not membership:
                messages.error(request, 'You are not a member of this group.')
                return redirect('group_list')

            is_admin = membership.role == GroupMember.ADMIN
            is_own = message.sender == user

            if not (is_admin or is_own):
                messages.error(request, 'You cannot delete this message.')
                return redirect('group_detail', group_id=message.group.id)

            message.soft_delete()
            return redirect('group_detail', group_id=message.group.id)

        if message.conversation:
            if user not in message.conversation.participants.all():
                messages.error(request, 'Access denied.')
                return redirect('conversation_list')

            if message.sender != user:
                messages.error(request, 'You can only delete your own messages.')
                return redirect('conversation_detail', conversation_id=message.conversation.id)

            message.soft_delete()
            return redirect('conversation_detail', conversation_id=message.conversation.id)

        messages.error(request, 'Message not found.')
        return redirect('group_list')


class UserProfileApiView(SessionLoginRequiredMixin, View):
    def get(self, request, user_id):
        current_user = get_current_user(request)
        target = get_object_or_404(UserModel, id=user_id)
        profile = getattr(target, 'profile', None)

        friendship = Friendship.objects.filter(
            sender=current_user, receiver=target, status=Friendship.ACCEPTED
        ).first() or Friendship.objects.filter(
            sender=target, receiver=current_user, status=Friendship.ACCEPTED
        ).first()

        conv_id = None
        for conv in current_user.conversations.all():
            if conv.participants.count() == 2 and conv.participants.filter(id=target.id).exists():
                conv_id = conv.id
                break

        return JsonResponse({
            'id': target.id,
            'username': target.username,
            'role': target.role,
            'avatar': profile.avatar.url if profile and profile.avatar else None,
            'bio': profile.bio or '' if profile else '',
            'phone': profile.phone or '' if profile else '',
            'status': profile.status if profile else 'offline',
            'coins': profile.coins if profile else 0,
            'is_friend': bool(friendship),
            'friendship_id': friendship.id if friendship else None,
            'conversation_id': conv_id,
            'is_self': target.id == current_user.id,
        })
    

class SearchGlobalUsersView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        q = request.GET.get('q', '').strip()

        if len(q) < 2:
            return JsonResponse({'users': []})

        users = UserModel.objects.filter(
            username__icontains=q
        ).exclude(id=user.id)[:8]

        result = []
        for u in users:
            friendship = Friendship.objects.filter(
                sender=user, receiver=u
            ).first() or Friendship.objects.filter(
                sender=u, receiver=user
            ).first()

            if friendship:
                if friendship.status == Friendship.ACCEPTED:
                    status = 'friends'
                elif friendship.status == Friendship.PENDING:
                    status = 'pending'
                else:
                    status = 'none'
            else:
                status = 'none'

            result.append({
                'id': u.id,
                'username': u.username,
                'role': u.role,
                'avatar': u.profile.avatar.url if hasattr(u, 'profile') and u.profile.avatar else None,
                'friendship_status': status,
            })

        return JsonResponse({'users': result})


class SendFriendRequestAjaxView(SessionLoginRequiredMixin, View):
    def post(self, request, user_id):
        user = get_current_user(request)
        target = get_object_or_404(UserModel, id=user_id)

        if target == user:
            return JsonResponse({'status': 'error', 'message': 'You cannot add yourself.'})

        exists = Friendship.objects.filter(
            sender=user, receiver=target
        ).exists() or Friendship.objects.filter(
            sender=target, receiver=user
        ).exists()

        if exists:
            return JsonResponse({'status': 'already', 'message': f'Request to {target.username} already exists.'})

        Friendship.objects.create(sender=user, receiver=target)
        return JsonResponse({'status': 'ok', 'message': f'Friend request sent to {target.username}!'})
