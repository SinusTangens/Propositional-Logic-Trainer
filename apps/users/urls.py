from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    PasswordChangeView,
    ResetProgressView,
    UpdateAvatarView,
    RandomizeAvatarView,
    UserViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # Auth Endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/password-change/', PasswordChangeView.as_view(), name='password-change'),
    path('auth/reset-progress/', ResetProgressView.as_view(), name='reset-progress'),
    
    # Avatar Endpoints
    path('auth/avatar/', UpdateAvatarView.as_view(), name='update-avatar'),
    path('auth/avatar/random/', RandomizeAvatarView.as_view(), name='randomize-avatar'),
    
    # ViewSet Routes
    path('', include(router.urls)),
]