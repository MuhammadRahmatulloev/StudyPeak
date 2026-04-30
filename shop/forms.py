from django import forms
from .models import Product, CoinTransaction, Achievement


class ProductCreateForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label='Product Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Premium Notes'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 4,
            'placeholder': 'Describe the product...'
        })
    )
    price = forms.IntegerField(
        label='Price (coins)',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 1,
            'placeholder': 'e.g. 50'
        })
    )
    type = forms.ChoiceField(
        label='Type',
        choices=Product.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    course_id = forms.IntegerField(
        label='Course',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    stock = forms.IntegerField(
        label='Stock',
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0,
            'placeholder': 'Available quantity'
        })
    )
    image = forms.ImageField(
        label='Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )


class ProductUpdateForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label='Product Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Product name'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 4,
            'placeholder': 'Describe the product...'
        })
    )
    price = forms.IntegerField(
        label='Price (coins)',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 1
        })
    )
    stock = forms.IntegerField(
        label='Stock',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0
        })
    )
    is_active = forms.BooleanField(
        label='Active',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )
    image = forms.ImageField(
        label='Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )


class GiveCoinsForm(forms.Form):
    student_id = forms.IntegerField(
        label='Student',
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    amount = forms.IntegerField(
        label='Amount',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 1,
            'placeholder': 'e.g. 10'
        })
    )
    description = forms.CharField(
        label='Reason',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Great work this week!'
        })
    )


class AchievementCreateForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label='Achievement Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Perfect Week'
        })
    )
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this achievement...'
        })
    )
    coin_reward = forms.IntegerField(
        label='Coin Reward',
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 0,
            'placeholder': 'e.g. 20'
        })
    )
    icon = forms.ImageField(
        label='Icon',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file'
        })
    )


class GrantAchievementForm(forms.Form):
    student_id = forms.IntegerField(
        label='Student',
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )