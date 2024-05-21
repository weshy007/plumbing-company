from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name="register"),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('login/', views.LoginAPIView.as_view(), name='login'),

    path('reset-email-request/', views.RequestPasswordResetEmail.as_view(), name="reset-email-request"),
    path('password-reset/<uidb64>/<token>/', views.PasswordTokenViewAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', views.SetNewPasswordAPIView.as_view(), name="password-reset-complete"),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/obtain/', TokenObtainPairView.as_view(), name='token_obtain'),

]