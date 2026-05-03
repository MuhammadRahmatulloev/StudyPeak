from django.urls import path
from .views import *

urlpatterns = [
    path('', ChatHomeView.as_view(), name='chat_home'),
    path('friends/', FriendListView.as_view(), name='friend_list'),
    path('friends/add/<int:user_id>/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friends/accept/<int:friendship_id>/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('friends/reject/<int:friendship_id>/', RejectFriendRequestView.as_view(), name='reject_friend_request'),
    path('friends/remove/<int:user_id>/', RemoveFriendView.as_view(), name='remove_friend'),
    path('users/<int:user_id>/profile/', UserProfileApiView.as_view(), name='user_profile_api'),

    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<int:conversation_id>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/start/<int:user_id>/', StartConversationView.as_view(), name='start_conversation'),

    path('groups/', GroupListView.as_view(), name='group_list'),
    path('groups/create/', GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:group_id>/', GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:group_id>/edit/', GroupUpdateView.as_view(), name='group_update'),
    path('groups/<int:group_id>/delete/', GroupDeleteView.as_view(), name='group_delete'),
    path('groups/<int:group_id>/leave/', GroupLeaveView.as_view(), name='group_leave'),
    path('groups/<int:group_id>/search-users/', SearchUsersView.as_view(), name='search_users'),

    path('groups/<int:group_id>/kick/<int:user_id>/', GroupKickMemberView.as_view(), name='group_kick_member'),
    path('groups/<int:group_id>/role/<int:user_id>/', GroupChangeMemberRoleView.as_view(), name='group_change_role'),

    path('groups/<int:group_id>/invite/', SendGroupInvitationView.as_view(), name='send_group_invitation'),
    path('invitations/<int:invitation_id>/accept/', AcceptGroupInvitationView.as_view(), name='accept_group_invitation'),
    path('invitations/<int:invitation_id>/reject/', RejectGroupInvitationView.as_view(), name='reject_group_invitation'),

    path('messages/<int:message_id>/pin/', PinMessageView.as_view(), name='pin_message'),
    path('messages/<int:message_id>/delete/', DeleteMessageView.as_view(), name='delete_message'),
    path('messages/<int:message_id>/edit/', EditMessageView.as_view(), name='edit_message'),

    path('friends/search/', SearchGlobalUsersView.as_view(), name='search_global_users'),
    path('friends/ajax/add/<int:user_id>/', SendFriendRequestAjaxView.as_view(), name='send_friend_request_ajax'),
]