from django import forms
from .models import UserModel, Profile


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. john_doe'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. john@gmail.com'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repeat your password'
        })
    )
    role = forms.ChoiceField(
        label='Role',
        choices=[
            (UserModel.STUDENT, 'Student'),
            (UserModel.TEACHER, 'Teacher'),
        ],
        widget=forms.Select(attrs={'class': 'form-input'})
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })
    )


class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        label='First Name',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your first name'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        label='Last Name',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your last name'
        })
    )
    bio = forms.CharField(
        label='Bio',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Tell something about yourself...'
        })
    )
    phone = forms.CharField(
        max_length=20,
        label='Phone',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+992 XX XXX XXXX'
        })
    )
    status = forms.ChoiceField(
        label='Status',
        choices=Profile.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    post_text = forms.CharField(
        label='Post Text',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 2,
            'placeholder': 'What\'s on your mind?'
        })
    )
    avatar = forms.ImageField(
        label='Avatar',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-file'})
    )


class ResetRequestForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email'
        })
    )


class OTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        label='Verification Code',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 6-digit code'
        })
    )


class NewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter new password'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repeat new password'
        })
    )


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter old password'
        })
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter new password'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repeat new password'
        })
    )