import django_filters
from .models import ActivityLog, LessonView, DailyStreak


class ActivityLogFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains', label='Username')
    action = django_filters.ChoiceFilter(choices=ActivityLog.ACTION_CHOICES, label='Action')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains', label='Description')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte', label='From')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte', label='To')

    class Meta:
        model = ActivityLog
        fields = []


class LessonViewFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains', label='Username')
    lesson = django_filters.CharFilter(field_name='lesson__title', lookup_expr='icontains', label='Lesson')
    date_from = django_filters.DateFilter(field_name='viewed_at', lookup_expr='gte', label='From')
    date_to = django_filters.DateFilter(field_name='viewed_at', lookup_expr='lte', label='To')

    class Meta:
        model = LessonView
        fields = []


class DailyStreakFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains', label='Username')
    min_streak = django_filters.NumberFilter(field_name='current_streak', lookup_expr='gte', label='Min Current Streak')
    max_streak = django_filters.NumberFilter(field_name='current_streak', lookup_expr='lte', label='Max Current Streak')

    class Meta:
        model = DailyStreak
        fields = []