import django_filters
from .models import Course, Enrollment, WeeklyJournal, Grade, Attendance


class CourseFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Course Name')
    teacher = django_filters.CharFilter(field_name='teacher__username', lookup_expr='icontains', label='Teacher')
    is_active = django_filters.BooleanFilter(field_name='is_active', label='Active')

    class Meta:
        model = Course
        fields = []


class EnrollmentFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(field_name='student__username', lookup_expr='icontains', label='Student')
    course = django_filters.CharFilter(field_name='course__name', lookup_expr='icontains', label='Course')
    status = django_filters.ChoiceFilter(choices=Enrollment.STATUS_CHOICES, label='Status')
    type = django_filters.ChoiceFilter(choices=Enrollment.TYPE_CHOICES, label='Type')

    class Meta:
        model = Enrollment
        fields = []


class WeeklyJournalFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(field_name='student__username', lookup_expr='icontains', label='Student')
    week_number = django_filters.NumberFilter(field_name='week_number', label='Week')
    coins_awarded = django_filters.BooleanFilter(field_name='coins_awarded', label='Coins Awarded')

    class Meta:
        model = WeeklyJournal
        fields = []


class GradeFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(field_name='student__username', lookup_expr='icontains', label='Student')
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte', label='Score From')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte', label='Score To')

    class Meta:
        model = Grade
        fields = []


class AttendanceFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(field_name='student__username', lookup_expr='icontains', label='Student')
    date = django_filters.DateFilter(field_name='date', label='Date')
    status = django_filters.ChoiceFilter(choices=Attendance.STATUS_CHOICES, label='Status')

    class Meta:
        model = Attendance
        fields = []