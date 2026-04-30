from django.contrib import admin
from .models import AIRequest, AIUsageLimit


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'context', 'is_blocked', 'created_at')
    list_filter = ('context', 'is_blocked')
    search_fields = ('user__username', 'question')


@admin.register(AIUsageLimit)
class AIUsageLimitAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_count', 'last_reset_date')
    search_fields = ('user__username',)