import django_filters
from .models import Product, Purchase, CoinTransaction, Achievement, UserAchievement


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Name')
    type = django_filters.ChoiceFilter(choices=Product.TYPE_CHOICES, label='Type')
    is_active = django_filters.BooleanFilter(field_name='is_active', label='Active')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Price From')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Price To')
    created_by = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains', label='Created By')
    course = django_filters.CharFilter(field_name='course__name', lookup_expr='icontains', label='Course')

    class Meta:
        model = Product
        fields = []


class PurchaseFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains', label='Username')
    product = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains', label='Product')
    status = django_filters.ChoiceFilter(choices=Purchase.STATUS_CHOICES, label='Status')
    date_from = django_filters.DateFilter(field_name='purchased_at', lookup_expr='gte', label='From')
    date_to = django_filters.DateFilter(field_name='purchased_at', lookup_expr='lte', label='To')

    class Meta:
        model = Purchase
        fields = []


class CoinTransactionFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains', label='Username')
    type = django_filters.ChoiceFilter(choices=CoinTransaction.TYPE_CHOICES, label='Type')
    reason = django_filters.ChoiceFilter(choices=CoinTransaction.REASON_CHOICES, label='Reason')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label='Amount From')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label='Amount To')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte', label='From')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte', label='To')

    class Meta:
        model = CoinTransaction
        fields = []


class AchievementFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Name')
    coin_reward_min = django_filters.NumberFilter(field_name='coin_reward', lookup_expr='gte', label='Reward From')
    coin_reward_max = django_filters.NumberFilter(field_name='coin_reward', lookup_expr='lte', label='Reward To')

    class Meta:
        model = Achievement
        fields = []


class UserAchievementFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains', label='Username')
    achievement = django_filters.CharFilter(field_name='achievement__name', lookup_expr='icontains', label='Achievement')
    date_from = django_filters.DateFilter(field_name='earned_at', lookup_expr='gte', label='From')
    date_to = django_filters.DateFilter(field_name='earned_at', lookup_expr='lte', label='To')

    class Meta:
        model = UserAchievement
        fields = []