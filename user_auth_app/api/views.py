from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class UserProfileList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny] 
    data = {}

    def post(self, request, format=None):
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