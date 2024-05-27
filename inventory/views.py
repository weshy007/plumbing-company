from django.shortcuts import render, get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from booking.models import Parts
from booking.serializers import PartsSerializer

# Create your views here.
class PartListCreateAPIView(generics.ListCreateAPIView):
    queryset = Parts.objects.all()
    serializer_class = PartsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class PartRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Parts.objects.all()
    serializer_class = PartsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        serializer.save(added_by=self.request.user)



class CheckPartAvailabilityAPIView(generics.GenericAPIView):
    serializer_class = PartsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        part_id = self.kwargs.get('pk')
        part = get_object_or_404(Parts, pk=part_id)
        
        return Response(
            {
                'name': part.name,
                'quantity': part.quantity
            }, status=status.HTTP_200_OK)