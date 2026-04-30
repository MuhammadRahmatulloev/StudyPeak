import django_filters
from .models import Assignment, Question, AssignmentSubmission, Answer


class AssignmentFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Title')
    type = django_filters.ChoiceFilter(choices=Assignment.TYPE_CHOICES, label='Type')
    is_published = django_filters.BooleanFilter(field_name='is_published', label='Published')
    teacher = django_filters.CharFilter(field_name='teacher__username', lookup_expr='icontains', label='Teacher')
    subject = django_filters.CharFilter(field_name='subject__title', lookup_expr='icontains', label='Subject')
    group = django_filters.CharFilter(field_name='group__name', lookup_expr='icontains', label='Group')
    deadline_from = django_filters.DateFilter(field_name='deadline', lookup_expr='gte', label='Deadline From')
    deadline_to = django_filters.DateFilter(field_name='deadline', lookup_expr='lte', label='Deadline To')

    class Meta:
        model = Assignment
        fields = []


class QuestionFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(field_name='text', lookup_expr='icontains', label='Text')
    type = django_filters.ChoiceFilter(choices=Question.TYPE_CHOICES, label='Type')
    assignment = django_filters.CharFilter(field_name='assignment__title', lookup_expr='icontains', label='Assignment')

    class Meta:
        model = Question
        fields = []


class SubmissionFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(field_name='student__username', lookup_expr='icontains', label='Student')
    assignment = django_filters.CharFilter(field_name='assignment__title', lookup_expr='icontains', label='Assignment')
    status = django_filters.ChoiceFilter(choices=AssignmentSubmission.STATUS_CHOICES, label='Status')
    score_min = django_filters.NumberFilter(field_name='total_score', lookup_expr='gte', label='Score From')
    score_max = django_filters.NumberFilter(field_name='total_score', lookup_expr='lte', label='Score To')
    submitted_from = django_filters.DateFilter(field_name='submitted_at', lookup_expr='gte', label='Submitted From')
    submitted_to = django_filters.DateFilter(field_name='submitted_at', lookup_expr='lte', label='Submitted To')

    class Meta:
        model = AssignmentSubmission
        fields = []


class AnswerFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(field_name='submission__student__username', lookup_expr='icontains', label='Student')
    question = django_filters.CharFilter(field_name='question__text', lookup_expr='icontains', label='Question')
    is_correct = django_filters.BooleanFilter(field_name='is_correct', label='Correct')

    class Meta:
        model = Answer
        fields = []