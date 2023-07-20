from .models import *
from django.db.models import Q
from rest_framework import status
from django.utils import timezone
from rest_framework import generics
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from .serializers import UserRegistrationSerializer,UserLoginSerializer,FriendRequestSerializer,SearchUserSerializer,CustomUserSerializer


# User Registration Api
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# User Login Api
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Perform any additional actions or return success response here
            return Response({'message': 'Login successful!', 'user_id': user.id}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Pagination 
class SearchUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# SerachUser Api(Email and Name wise) 
class SearchUserAPIView(APIView):
    def get(self, request):
        keyword = request.query_params.get('q', None)
        if not keyword:
            return Response({'message': 'No search keyword provided.'}, status=status.HTTP_400_BAD_REQUEST)

        users = CustomUser.search_users(keyword)

        paginator = SearchUserPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = SearchUserSerializer(paginated_users, many=True)

        return paginator.get_paginated_response(serializer.data)
    
class FriendRequestView(APIView):
    def post(self, request):
        serializer = FriendRequestSerializer(data=request.data)

        if serializer.is_valid():
            sender = serializer.validated_data['sender']
            receiver = serializer.validated_data['receiver']

            # Check if the sender and receiver are different users
            if sender == receiver:
                return Response({'message': 'Cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the sender and receiver are already friends
            if Friendship.objects.filter(Q(user1=sender, user2=receiver) | Q(user1=receiver, user2=sender)).exists():
                return Response({'message': 'Already friends.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the sender has already sent three friend requests within a minute
            now = timezone.now()
            one_minute_ago = now - timezone.timedelta(minutes=1)

            sent_friend_requests_count = FriendRequest.objects.filter(sender=sender, timestamp__gte=one_minute_ago).count()

            if sent_friend_requests_count >= 3:
                return Response({'message': 'You have exceeded the limit of 3 friend requests per minute.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Create the friend request
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Accept or reject friend requests
        try:
            useremail = CustomUser.objects.get(email=request.data['request_id'])
            friend_request = FriendRequest.objects.get(receiver=useremail.id)
        except FriendRequest.DoesNotExist:
            return Response({'message': 'Friend request does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FriendRequestSerializer(friend_request, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get a list of friends (users who have accepted friend requests)
class FriendshipListView(APIView):
    def get(self, request):
        user = 1 #request.user
        friends = CustomUser.objects.filter(
            Q(sent_friend_requests__receiver=user, sent_friend_requests__status='accepted') |
            Q(received_friend_requests__sender=user, received_friend_requests__status='accepted')
        ).distinct()
        serializer = CustomUserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# List pending friend requests (pending friend requests)
class PendingFriendRequestsView(APIView):
    def get(self, request):
        user = 1 # request.user  
        pending_requests = CustomUser.objects.filter(
            Q(sent_friend_requests__receiver=user, sent_friend_requests__status='pending') |
            Q(received_friend_requests__sender=user, received_friend_requests__status='pending')
        ).distinct()
        serializer = CustomUserSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# List reject friend requests (reject friend requests)
class RejectFriendRequestsView(APIView):
    def get(self, request):
        user = 1 # request.user  
        pending_requests = CustomUser.objects.filter(
            Q(sent_friend_requests__receiver=user, sent_friend_requests__status='rejected') |
            Q(received_friend_requests__sender=user, received_friend_requests__status='rejected')
        ).distinct()
        serializer = CustomUserSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)