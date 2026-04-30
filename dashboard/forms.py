from django import forms
from .models import ActivityLog


class ActivityLogFilterForm(forms.Form):
    user = forms.CharField(
        max_length=100,
        label='Username',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Filter by username',
        })
    )
    action = forms.ChoiceField(
        label='Action',
        required=False,
        choices=[('', 'All')] + ActivityLog.ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    date_from = forms.DateField(
        label='From',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )
    date_to = forms.DateField(
        label='To',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )


class StudentProgressFilterForm(forms.Form):
    student_id = forms.IntegerField(
        label='Student ID',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter student ID',
        })
    )


class LessonViewFilterForm(forms.Form):
    user = forms.CharField(
        max_length=100,
        label='Username',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Filter by username',
        })
    )
    lesson = forms.CharField(
        max_length=200,
        label='Lesson',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Filter by lesson title',
        })
    )
    date_from = forms.DateField(
        label='From',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )
    date_to = forms.DateField(
        label='To',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        })
    )