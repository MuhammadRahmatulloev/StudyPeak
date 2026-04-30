import django_filters
from .models import Subject, Lesson, Material


class SubjectFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Title')
    teacher = django_filters.CharFilter(field_name='teacher__username', lookup_expr='icontains', label='Teacher')
    group = django_filters.CharFilter(field_name='group__name', lookup_expr='icontains', label='Group')
    is_active = django_filters.BooleanFilter(field_name='is_active', label='Active')

    class Meta:
        model = Subject
        fields = []


class LessonFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Title')
    subject = django_filters.CharFilter(field_name='subject__title', lookup_expr='icontains', label='Subject')

    class Meta:
        model = Lesson
        fields = []


class MaterialFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Title')
    type = django_filters.ChoiceFilter(choices=Material.TYPE_CHOICES, label='Type')
    lesson = django_filters.CharFilter(field_name='lesson__title', lookup_expr='icontains', label='Lesson')

    class Meta:
        model = Material
        fields = []