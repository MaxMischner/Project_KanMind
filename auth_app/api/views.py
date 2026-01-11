"""API views for user authentication and profile management.

This module contains views for user registration, profile management,
and related user operations.
"""

from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class UserProfileList(generics.ListCreateAPIView):
    """API view for listing and creating user profiles.

    GET /api/profiles/ - List all user profiles.
    POST /api/profiles/ - Create a new user profile.
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting user profiles.

    GET /api/profiles/{id}/ - Retrieve a specific user profile.
    PATCH /api/profiles/{id}/ - Update a user profile.
    DELETE /api/profiles/{id}/ - Delete a user profile.
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView(APIView):
    """API view for user registration.

    POST /api/auth/registration/ - Register a new user account.

    Creates a new user with email-based authentication and returns
    an authentication token for immediate login.
    """

    permission_classes = [AllowAny]
    data = {}

    def post(self, request, format=None):
        """Handle user registration requests.

        Creates a new user account and generates an authentication token.

        Args:
            request (Request): HTTP request with registration data.
            format (str): Optional format parameter.

        Returns:
            Response: Success data with token and user info, or validation errors.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'user_id': saved_account.id,
                'email': saved_account.email,
                'fullname': saved_account.get_full_name() or saved_account.username
            }
        else:
            data = serializer.errors

        return Response(data)
