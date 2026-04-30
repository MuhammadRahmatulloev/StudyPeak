from django.db import models
from django.utils import timezone
from accounts.models import UserModel


class Friendship(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username} [{self.status}]'


class Conversation(models.Model):
    participants = models.ManyToManyField(UserModel, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Conversation [{self.pk}]'


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='group_avatars/', null=True, blank=True)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='owned_groups')
    members = models.ManyToManyField(UserModel, through='GroupMember', related_name='chat_groups')
    is_study_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    ADMIN = 'admin'
    MEMBER = 'member'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f'{self.user.username} in {self.group.name} [{self.role}]'


class GroupInvitation(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='sent_invitations')
    receiver = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='received_invitations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'receiver')

    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username} в {self.group.name}'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        super().delete()

    def __str__(self):
        place = f'Group:{self.group}' if self.group else f'DM:{self.conversation}'
        return f'{self.sender.username} → {place}'