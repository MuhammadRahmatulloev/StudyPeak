import django_filters
from .models import NewsFeed


class NewsFeedFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Title')
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains', label='Author')
    type = django_filters.ChoiceFilter(choices=NewsFeed.TYPE_CHOICES, label='Type')
    is_active = django_filters.BooleanFilter(field_name='is_active', label='Active')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte', label='From')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte', label='To')

    class Meta:
        model = NewsFeed
        fields = []