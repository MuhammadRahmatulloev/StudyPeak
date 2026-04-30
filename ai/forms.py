from django import forms
from .models import AIRequest


class AIQuestionForm(forms.Form):
    question = forms.CharField(
        label='Ask AI',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Ask me anything about this topic...'
        })
    )
    context = forms.ChoiceField(
        label='Context',
        choices=AIRequest.CONTEXT_CHOICES,
        required=False,
        widget=forms.HiddenInput()
    )
    lesson_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    assignment_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )