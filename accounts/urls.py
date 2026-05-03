from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path('verify/', verify_otp_view, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('notifications/', NotificationListView.as_view(), name='notification_list'),

    path('reset/', reset_request_view, name='reset_request'),
    path('reset/verify/', reset_verify_otp_view, name='reset_verify_otp'),
    path('reset/new-password/', reset_new_password_view, name='reset_new_password'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/password/', ChangePasswordView.as_view(), name='change_password'),
]