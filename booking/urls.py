from django.urls import path

from . import views

urlpatterns = [
    path('repair-request/', views.RepairRequestCreateAPIView.as_view(), name='repair-request-create'),
]