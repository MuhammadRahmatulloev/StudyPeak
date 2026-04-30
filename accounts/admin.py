from django.contrib import admin
from .models import UserModel, Profile, Notification


@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'coins', 'phone', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'phone')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('user__username',)