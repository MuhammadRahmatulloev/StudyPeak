from django.db import models
from accounts.models import UserModel


class Product(models.Model):
    GLOBAL = 'global'
    COURSE = 'course'

    TYPE_CHOICES = [
        (GLOBAL, 'Global'),
        (COURSE, 'Course'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    price = models.PositiveIntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=GLOBAL)
    course = models.ForeignKey('crm.Course', on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='created_products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} | {self.price} coins'


class Purchase(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} → {self.product.name} [{self.status}]'


class CoinTransaction(models.Model):
    EARN = 'earn'
    SPEND = 'spend'

    TYPE_CHOICES = [
        (EARN, 'Earn'),
        (SPEND, 'Spend'),
    ]

    WEEKLY_SCORE = 'weekly_score'
    TEACHER_GIFT = 'teacher_gift'
    ACHIEVEMENT = 'achievement'
    PURCHASE = 'purchase'

    REASON_CHOICES = [
        (WEEKLY_SCORE, 'Weekly Score'),
        (TEACHER_GIFT, 'Teacher Gift'),
        (ACHIEVEMENT, 'Achievement'),
        (PURCHASE, 'Purchase'),
    ]

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='coin_transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = '+' if self.type == self.EARN else '-'
        return f'{self.user.username} | {sign}{self.amount} [{self.reason}]'


class Achievement(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/', null=True, blank=True)
    coin_reward = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} | {self.coin_reward} coins'


class UserAchievement(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f'{self.user.username} | {self.achievement.name}'