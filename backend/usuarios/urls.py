from django.urls import path
from .views import RegisterView
from .views import UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
