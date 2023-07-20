# myapp/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('search/', SearchUserAPIView.as_view(), name='search-users'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friends/', FriendshipListView.as_view(), name='friend-list'),
    path('pending-friend-requests/', PendingFriendRequestsView.as_view(), name='pending-requests'),
    path('reject-friend-requests/',RejectFriendRequestsView.as_view(), name='reject-requests')
]
