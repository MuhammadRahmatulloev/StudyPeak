from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('<int:product_id>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('<int:product_id>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('<int:product_id>/buy/', PurchaseProductView.as_view(), name='purchase_product'),

    path('purchases/', PurchaseListView.as_view(), name='purchase_list'),
    path('coins/', CoinTransactionListView.as_view(), name='coin_transaction_list'),
    path('coins/give/', GiveCoinsView.as_view(), name='give_coins'),

    path('achievements/', AchievementListView.as_view(), name='achievement_list'),
    path('achievements/create/', AchievementCreateView.as_view(), name='achievement_create'),
    path('achievements/<int:achievement_id>/delete/', AchievementDeleteView.as_view(), name='achievement_delete'),
    path('achievements/<int:achievement_id>/grant/', GrantAchievementView.as_view(), name='grant_achievement'),
    path('achievements/my/', UserAchievementListView.as_view(), name='user_achievement_list'),
]