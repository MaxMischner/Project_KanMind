"""Serializers for user authentication and registration.

This module contains serializers for user registration, authentication,
and profile management. Includes custom email-based authentication.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information.

    Handles serialization of basic user profile data.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with email and fullname.

    Handles user registration with the following features:
    - Email-based authentication (email used as username)
    - Fullname field that gets split into first_name and last_name
    - Password confirmation validation
    - Email uniqueness validation

    Fields:
        fullname (str): User's full name (write-only, gets split).
        email (str): User's email address (becomes username).
        password (str): User's password (write-only).
        repeated_password (str): Password confirmation (write-only).
    """

    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def _validate_passwords(self, password, repeated_password):
        """Validate that password and repeated_password match.

        Args:
            password (str): The password entered by user.
            repeated_password (str): The password confirmation.

        Raises:
            ValidationError: If passwords don't match.
        """
        if password != repeated_password:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

    def _validate_email_unique(self, email):
        """Validate that email is not already in use.

        Checks both email and username fields since email is used as username.

        Args:
            email (str): The email address to validate.

        Raises:
            ValidationError: If email is already registered.
        """
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email is already in use.'})
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({'email': 'Email is already in use.'})

    def _validate_required_fields(self, email, fullname, password, repeated_password):
        """Validate that all required fields are provided.

        Args:
            email (str): User's email address.
            fullname (str): User's full name.
            password (str): User's password.
            repeated_password (str): Password confirmation.

        Raises:
            ValidationError: If any required field is missing.
        """
        if email is None:
            raise serializers.ValidationError({'email': 'Email is required.'})
        if fullname is None:
            raise serializers.ValidationError({'fullname': 'Fullname is required.'})
        if password is None:
            raise serializers.ValidationError({'password': 'Password is required.'})
        if repeated_password is None:
            raise serializers.ValidationError(
                {'repeated_password': 'Repeated password is required.'})

    def _split_fullname(self, fullname):
        """Split full name into first and last name.

        Args:
            fullname (str): The user's full name.

        Returns:
            tuple: (first_name, last_name) where last_name may be empty.
        """
        fullname_parts = fullname.strip().split(' ', 1)
        first_name = fullname_parts[0]
        last_name = fullname_parts[1] if len(fullname_parts) > 1 else ''
        return first_name, last_name

    def _create_user_account(self, email, first_name, last_name, password):
        """Create and save a new user account.

        Args:
            email (str): User's email (used as username).
            first_name (str): User's first name.
            last_name (str): User's last name.
            password (str): User's password (will be hashed).

        Returns:
            User: The newly created user instance.
        """
        account = User(username=email, email=email, first_name=first_name, last_name=last_name)
        account.set_password(password)
        account.save()
        return account

    def save(self, **kwargs):
        """Create a new user account after validation.

        Orchestrates the validation and creation process:
        1. Validates all required fields are present
        2. Validates passwords match
        3. Validates email is unique
        4. Splits fullname into first and last name
        5. Creates the user account

        Args:
            **kwargs: Additional keyword arguments (unused).

        Returns:
            User: The newly created user instance.

        Raises:
            ValidationError: If validation fails at any step.
        """
        fullname = self.validated_data['fullname']
        email = self.validated_data['email']
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']

        self._validate_required_fields(email, fullname, password, repeated_password)
        self._validate_passwords(password, repeated_password)
        self._validate_email_unique(email)

        first_name, last_name = self._split_fullname(fullname)
        return self._create_user_account(email, first_name, last_name, password)


class EmailAuthTokenSerializer(serializers.Serializer):
    """Custom authentication serializer using email instead of username.

    Replaces DRF's default username-based authentication with email-based
    authentication. Validates user credentials and returns the user object.

    Fields:
        email (str): User's email address.
        password (str): User's password.
    """

    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def _get_user_by_email(self, email):
        """Retrieve user by email address.

        Args:
            email (str): The email address to look up.

        Returns:
            User: The user with the given email.

        Raises:
            ValidationError: If user with email doesn't exist.
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Unable to log in with provided credentials.')

    def _verify_password(self, user, password):
        """Verify that the password is correct for the user.

        Args:
            user (User): The user to verify password for.
            password (str): The password to check.

        Raises:
            ValidationError: If password is incorrect.
        """
        if not user.check_password(password):
            raise serializers.ValidationError('Unable to log in with provided credentials.')

    def validate(self, attrs):
        """Validate email and password credentials.

        Checks that both email and password are provided, looks up the user
        by email, and verifies the password is correct.

        Args:
            attrs (dict): Dictionary containing 'email' and 'password'.

        Returns:
            dict: The validated attributes with 'user' object added.

        Raises:
            ValidationError: If credentials are missing or invalid.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if not (email and password):
            raise serializers.ValidationError('Must include "email" and "password".')

        user = self._get_user_by_email(email)
        self._verify_password(user, password)
        attrs['user'] = user
        return attrs


class CostomLoginView(ObtainAuthToken):
    """Custom login view using email-based authentication.

    Extends DRF's ObtainAuthToken to use EmailAuthTokenSerializer
    for email-based authentication instead of username-based.
    Allows unauthenticated access for login.
    """

    serializer_class = EmailAuthTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        data = {}
        if serializers.is_valid():
            user = serializers.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            data['user_id'] = user.id
            data['email'] = user.email
            data['fullname'] = user.get_full_name() or user.username
        else:
            data = serializers.errors

        return Response(data)
