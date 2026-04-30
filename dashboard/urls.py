from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('activity/', ActivityLogListView.as_view(), name='activity_log_list'),
    path('lessons/viewed/', LessonViewListView.as_view(), name='lesson_view_list'),
    path('streak/', StreakView.as_view(), name='streak'),
    path('progress/', StudentProgressView.as_view(), name='student_progress'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
]