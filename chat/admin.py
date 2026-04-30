from django.contrib import admin
from .models import Friendship, Conversation, Group, GroupMember, GroupInvitation, Message


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('sender__username', 'receiver__username')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_study_group', 'created_at')
    list_filter = ('is_study_group',)
    search_fields = ('name', 'owner__username')


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'group__name')


@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'group', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('sender__username', 'receiver__username', 'group__name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'group', 'conversation', 'is_pinned', 'is_deleted', 'created_at')
    list_filter = ('is_pinned', 'is_deleted')
    search_fields = ('sender__username', 'content')


admin.site.register(Conversation)