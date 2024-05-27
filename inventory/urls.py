from django.urls import path

from . import views

urlpatterns = [
    path('inventory/parts/', views.PartListCreateAPIView.as_view(), name='part-list-create'),
    path('inventory/parts/<int:pk>/', views.PartRetrieveUpdateDestroyAPIView.as_view(), name='part-detail'),
    path('inventory/parts/check/<int:pk>/', views.CheckPartAvailabilityAPIView.as_view(), name='check-part-availability'),
]