from django.urls import path
from .views import *

urlpatterns = [
    path('ask/', AIRequestView.as_view(), name='ai_ask'),
    path('history/', AIHistoryView.as_view(), name='ai_history'),
    path('history/<int:request_id>/delete/', AIHistoryDeleteView.as_view(), name='ai_history_delete'),
    path('limits/', AIUsageLimitListView.as_view(), name='ai_usage_limits'),
]