from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name="register"),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('login/', views.LoginAPIView.as_view(), name='login'),


]