from django import forms
from .models import Subject, Lesson, Material


class SubjectCreateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Mathematics'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this subject...'
        })
    )
    group_id = forms.IntegerField(
        label='Group',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    cover = forms.ImageField(
        label='Cover Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )


class SubjectUpdateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Subject title'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this subject...'
        })
    )
    group_id = forms.IntegerField(
        label='Group',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    is_active = forms.BooleanField(
        label='Active',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )
    cover = forms.ImageField(
        label='Cover Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )


class LessonCreateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Introduction to Algebra'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this lesson...'
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


class LessonUpdateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Lesson title'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this lesson...'
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


class MaterialCreateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Chapter 1 PDF'
        })
    )
    type = forms.ChoiceField(
        label='Type',
        choices=Material.TYPE_CHOICES,
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
    url = forms.URLField(
        label='URL',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-input',
            'placeholder': 'https://...'
        })
    )
    content = forms.CharField(
        label='Text Content',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 5,
            'placeholder': 'Write text content here...'
        })
    )
    file = forms.FileField(
        label='File',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )


class MaterialUpdateForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='Title',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Material title'
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
    url = forms.URLField(
        label='URL',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-input',
            'placeholder': 'https://...'
        })
    )
    content = forms.CharField(
        label='Text Content',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 5,
            'placeholder': 'Write text content here...'
        })
    )
    file = forms.FileField(
        label='File',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )