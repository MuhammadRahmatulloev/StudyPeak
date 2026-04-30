from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('news/', NewsFeedListView.as_view(), name='newsfeed_list'),
    path('news/create/', NewsFeedCreateView.as_view(), name='newsfeed_create'),
    path('news/<int:post_id>/', NewsFeedDetailView.as_view(), name='newsfeed_detail'),
    path('news/<int:post_id>/update/', NewsFeedUpdateView.as_view(), name='newsfeed_update'),
    path('news/<int:post_id>/delete/', NewsFeedDeleteView.as_view(), name='newsfeed_delete'),

    path('notifications/<int:notification_id>/read/', NotificationMarkReadView.as_view(), name='notification_read'),
    path('notifications/read-all/', NotificationMarkAllReadView.as_view(), name='notification_read_all'),
]