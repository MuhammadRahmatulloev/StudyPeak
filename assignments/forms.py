from django import forms
from .models import Assignment, Question, Choice


class AssignmentCreateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Assignment title...'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 4,
            'placeholder': 'Describe the assignment...'
        })
    )
    subject_id = forms.IntegerField(
        label='Subject',
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    group_id = forms.IntegerField(
        label='Group',
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    type = forms.ChoiceField(
        label='Type',
        choices=Assignment.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    deadline = forms.DateTimeField(
        label='Deadline',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-input',
            'type': 'datetime-local'
        })
    )
    time_limit = forms.IntegerField(
        label='Time Limit (minutes)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Only for quiz...',
            'min': 1
        })
    )


class AssignmentUpdateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Assignment title...'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 4,
            'placeholder': 'Describe the assignment...'
        })
    )
    type = forms.ChoiceField(
        label='Type',
        choices=Assignment.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    deadline = forms.DateTimeField(
        label='Deadline',
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-input',
            'type': 'datetime-local'
        })
    )
    time_limit = forms.IntegerField(
        label='Time Limit (minutes)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Only for quiz...',
            'min': 1
        })
    )


class QuestionCreateForm(forms.Form):
    text = forms.CharField(
        label='Question Text',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Write your question...'
        })
    )
    type = forms.ChoiceField(
        label='Question Type',
        choices=Question.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    order = forms.IntegerField(
        label='Order',
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0
        })
    )
    score = forms.IntegerField(
        label='Score',
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 1
        })
    )


class QuestionUpdateForm(forms.Form):
    text = forms.CharField(
        label='Question Text',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Write your question...'
        })
    )
    type = forms.ChoiceField(
        label='Question Type',
        choices=Question.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    order = forms.IntegerField(
        label='Order',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0
        })
    )
    score = forms.IntegerField(
        label='Score',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 1
        })
    )


class ChoiceCreateForm(forms.Form):
    text = forms.CharField(
        max_length=300,
        label='Choice Text',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter choice...'
        })
    )
    is_correct = forms.BooleanField(
        label='Correct Answer',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )


class ChoiceUpdateForm(forms.Form):
    text = forms.CharField(
        max_length=300,
        label='Choice Text',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter choice...'
        })
    )
    is_correct = forms.BooleanField(
        label='Correct Answer',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )


class GradeTextAnswerForm(forms.Form):
    score = forms.IntegerField(
        label='Score',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0
        })
    )
    is_correct = forms.BooleanField(
        label='Mark as Correct',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )