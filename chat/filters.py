import django_filters
from .models import Group, Message, Friendship


class GroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Group Name')
    is_study_group = django_filters.BooleanFilter(field_name='is_study_group', label='Study Group')
    owner = django_filters.CharFilter(field_name='owner__username', lookup_expr='icontains', label='Owner')

    class Meta:
        model = Group
        fields = []


class MessageFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(field_name='content', lookup_expr='icontains', label='Content')
    sender = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains', label='Sender')
    is_pinned = django_filters.BooleanFilter(field_name='is_pinned', label='Pinned')
    is_deleted = django_filters.BooleanFilter(field_name='is_deleted', label='Deleted')

    class Meta:
        model = Message
        fields = []


class FriendshipFilter(django_filters.FilterSet):
    sender = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains', label='Sender')
    receiver = django_filters.CharFilter(field_name='receiver__username', lookup_expr='icontains', label='Receiver')
    status = django_filters.ChoiceFilter(choices=Friendship.STATUS_CHOICES, label='Status')

    class Meta:
        model = Friendship
        fields = []