from django.urls import path

from . import views

urlpatterns = [
    path('repair-request/', views.RepairRequestCreateAPIView.as_view(), name='repair-request-create'),
    path('otp/generate/', views.OTPGenerateAPIView.as_view(), name='otp-generate'),
    path('otp/verify/', views.OTPVerifyAPIView.as_view(), name='otp-verify'),
]