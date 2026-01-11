from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        fullname = self.validated_data['fullname']
        email = self.validated_data['email']
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']

        if password != repeated_password:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email is already in use.'})
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({'email': 'Email is already in use.'})
        if email is None:
            raise serializers.ValidationError({'email': 'Email is required.'})
        if fullname is None:
            raise serializers.ValidationError({'fullname': 'Fullname is required.'})
        if password is None:
            raise serializers.ValidationError({'password': 'Password is required.'})
        if repeated_password is None:
            raise serializers.ValidationError({'repeated_password': 'Repeated password is required.'})

        # Split fullname into first_name and last_name
        fullname_parts = fullname.strip().split(' ', 1)
        first_name = fullname_parts[0]
        last_name = fullname_parts[1] if len(fullname_parts) > 1 else ''

        account = User(username=email, email=email, first_name=first_name, last_name=last_name)
        account.set_password(password)
        account.save()
        return account
    
class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            if not user.check_password(password):
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        attrs['user'] = user
        return attrs

class CostomLoginView(ObtainAuthToken):
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
        