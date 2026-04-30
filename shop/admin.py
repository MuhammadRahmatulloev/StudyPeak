from django.contrib import admin
from .models import Product, Purchase, CoinTransaction, Achievement, UserAchievement


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'type', 'stock', 'is_active', 'created_by')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'status', 'purchased_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'product__name')


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'reason', 'amount', 'created_at')
    list_filter = ('type', 'reason')
    search_fields = ('user__username',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'coin_reward', 'created_at')
    search_fields = ('name',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    search_fields = ('user__username', 'achievement__name')