from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name="register"),
    path('auth/verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify'),


]