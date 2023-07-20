# myapp/serializers.py
import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import EmailValidator
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser,FriendRequest, Friendship







class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(validators=[EmailValidator()])

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'name', 'last_name']
        
    
    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data.get('name', '')
        last_name = validated_data.get('last_name', '')
        
        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user:
            raise serializers.ValidationError('User with this email already exists.')
            

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            name=first_name,
            last_name=last_name
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid email or password.')

            if not user.is_active:
                raise serializers.ValidationError('User account is inactive.')

        else:
            raise serializers.ValidationError('Both email and password are required.')

        data['user'] = user
        return data

class SearchUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','name']

# class FriendRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FriendRequest
#         fields = ['sender', 'receiver', 'timestamp', 'status']

#     def create(self, validated_data):
#         sender = validated_data['sender']
#         receiver = validated_data['receiver']

#         # Check if the friend request already exists
#         friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()

#         if friend_request:
#             raise serializers.ValidationError('Friend request already exists.')

#         # Create the friend request
#         friend_request = FriendRequest.objects.create(sender=sender, receiver=receiver)
#         return friend_request

#     def update(self, instance, validated_data):
#         instance.status = validated_data.get('status', instance.status)
#         instance.save()
#         return instance

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['sender', 'receiver', 'timestamp', 'status']

    def to_internal_value(self, data):
        # Convert email addresses to user IDs for sender and receiver fields
        try:
            sender_email = data.get('sender')
            receiver_email = data.get('receiver')

            if sender_email:
                sender = CustomUser.objects.get(email=sender_email)
                data['sender'] = sender.id

            if receiver_email:
                receiver = CustomUser.objects.get(email=receiver_email)
                data['receiver'] = receiver.id
        except ObjectDoesNotExist:
            raise serializers.ValidationError('User with the provided email does not exist.')

        return super().to_internal_value(data)

    def create(self, validated_data):
        sender = validated_data['sender']
        receiver = validated_data['receiver']

        # Check if the friend request already exists
        friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()

        if friend_request:
            raise serializers.ValidationError('Friend request already exists.')

        # Create the friend request
        friend_request = FriendRequest.objects.create(sender=sender, receiver=receiver)
        return friend_request

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
    

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email']  # Add any other fields you want to include


class FriendshipSerializer(serializers.ModelSerializer):
    user1 = CustomUserSerializer()
    user2 = CustomUserSerializer()

    class Meta:
        model = Friendship
        fields = ['user1', 'user2', 'timestamp']
        