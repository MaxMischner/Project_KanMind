from django.urls import path

from user_auth_app.api.serializers import CostomLoginView
from .views import RegistrationView, UserProfileList, UserProfileDetail 
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CostomLoginView.as_view(), name='login'),
]

