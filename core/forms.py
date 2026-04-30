from django import forms
from .models import NewsFeed


class NewsFeedCreateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Post title...'
        })
    )
    content = forms.CharField(
        label='Content',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 5,
            'placeholder': 'Write something...'
        })
    )
    type = forms.ChoiceField(
        label='Type',
        choices=NewsFeed.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    image = forms.ImageField(
        label='Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )


class NewsFeedUpdateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Post title...'
        })
    )
    content = forms.CharField(
        label='Content',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 5,
            'placeholder': 'Write something...'
        })
    )
    type = forms.ChoiceField(
        label='Type',
        choices=NewsFeed.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    image = forms.ImageField(
        label='Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )
    is_active = forms.BooleanField(
        label='Active',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )