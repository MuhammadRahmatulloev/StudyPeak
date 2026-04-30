import django_filters
from .models import UserModel


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains', label='Username')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains', label='Email')
    role = django_filters.ChoiceFilter(choices=UserModel.ROLE_CHOICES, label='Role')

    class Meta:
        model = UserModel
        fields = []