from django import forms
from .models import Group, GroupMember, Message


class GroupCreateForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Group Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. Python Class 2025'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this group...'
        })
    )
    avatar = forms.ImageField(
        label='Group Avatar',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-file'})
    )
    is_study_group = forms.BooleanField(
        label='Study Group',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )


class GroupUpdateForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Group Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Group name'
        })
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'Describe this group...'
        })
    )
    avatar = forms.ImageField(
        label='Group Avatar',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-file'})
    )
    is_study_group = forms.BooleanField(
        label='Study Group',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )


class MessageForm(forms.Form):
    content = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 2,
            'placeholder': 'Write a message...'
        })
    )


class SendFriendRequestForm(forms.Form):
    user_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )


class SendGroupInvitationForm(forms.Form):
    user_id = forms.IntegerField(
        label='User ID',
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter user ID'
        })
    )


class GroupChangeMemberRoleForm(forms.Form):
    role = forms.ChoiceField(
        label='Role',
        choices=GroupMember.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )