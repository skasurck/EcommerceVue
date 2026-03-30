# backend/usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserProfileView, ChangePasswordView, LoginView, AdminUserViewSet, ProfilePhotoView, Login2FAView, Setup2FAView, Status2FAView
from rest_framework_simplejwt.views import TokenRefreshView  # 👈 agrega esto

router = DefaultRouter()
router.register('admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/login/2fa/', Login2FAView.as_view(), name='login_2fa'),
    path('auth/2fa/setup/', Setup2FAView.as_view(), name='2fa_setup'),
    path('auth/2fa/status/', Status2FAView.as_view(), name='2fa_status'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),  # 👈 alias compatible
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/foto/', ProfilePhotoView.as_view(), name='profile_foto'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('', include(router.urls)),
]
