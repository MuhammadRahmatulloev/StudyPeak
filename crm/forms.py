from django import forms
from .models import Course, CoursePeriod, Enrollment, WeeklyJournal, Grade, Attendance


class CourseCreateForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label='Course Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Python Programming'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this course...'
        })
    )


class CourseUpdateForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label='Course Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Course name'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this course...'
        })
    )
    is_active = forms.BooleanField(
        label='Active',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )


class CoursePeriodForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Period Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Month 1'
        })
    )
    order = forms.IntegerField(
        label='Order',
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 1
        })
    )
    start_date = forms.DateField(
        label='Start Date',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        label='End Date',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )


class EnrollInviteForm(forms.Form):
    student_id = forms.IntegerField(
        label='Student ID',
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter student ID'
        })
    )


class WeeklyJournalForm(forms.Form):
    week = forms.IntegerField(
        label='Week Number',
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 1
        })
    )


class WeeklyJournalRowForm(forms.Form):
    base_score = forms.IntegerField(
        label='Base Score',
        initial=0,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0,
            'max': 100
        })
    )
    bonus_score = forms.IntegerField(
        label='Bonus Score',
        initial=0,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0,
            'max': 10
        })
    )
    teacher_comment = forms.CharField(
        label='Comment',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Optional comment...'
        })
    )


class GradeForm(forms.Form):
    student_id = forms.IntegerField(
        label='Student',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    submission_id = forms.IntegerField(
        label='Submission',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    score = forms.IntegerField(
        label='Score',
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0
        })
    )
    teacher_comment = forms.CharField(
        label='Comment',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 2,
            'placeholder': 'Optional comment...'
        })
    )


class AttendanceDateForm(forms.Form):
    date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )


class AttendanceRowForm(forms.Form):
    status = forms.ChoiceField(
        label='Status',
        choices=Attendance.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )