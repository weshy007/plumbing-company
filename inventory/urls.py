from django.urls import path

from . import views

urlpatterns = [
    path('parts/', views.PartListCreateAPIView.as_view(), name='part-list-create'),
    path('parts/<int:pk>/', views.PartRetrieveUpdateDestroyAPIView.as_view(), name='part-detail'),
    path('parts/check/<int:pk>/', views.CheckPartAvailabilityAPIView.as_view(), name='check-part-availability'),
    
    # Out of stock urls
    path('parts/out_of_stock/', views.CheckOutOfStockPartsAPIView.as_view(), name='check-out-of-stock-parts'),
    path('notify_staff/', views.NotifyStaffAPIView.as_view(), name='notify-staff')

]