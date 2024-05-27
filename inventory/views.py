from django.shortcuts import render, get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from booking.models import Parts, RepairRequest
from booking.serializers import PartsSerializer, RepairRequestSerializer

from authentication.email import Util

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
    

# Outof Stock handling
class CheckOutOfStockPartsAPIView(generics.ListAPIView):
    serializer_class = RepairRequestSerializer
    queryset = RepairRequest.objects.all()

    def get(self, request, *args, **kwargs):
        out_of_stock_parts = []
        
        for request in self.queryset():
            for part in request.parts.all():
                if part.quantity <= 0:
                    out_of_stock_parts.append(part)


        if out_of_stock_parts:
            serialaizer = PartsSerializer(out_of_stock_parts, many=True)
            return Response(serialaizer.data, status=status.HTTP_200_OK)

        return Response({'message': 'No parts are out of stock'}, status=status.HTTP_200_OK) 
    

# Notify Staff
class NotifyStaffAPIView(APIView):
    def post(self, request):
        out_of_stock_parts = Parts.objects.filter(quantity__lte=0)
        if out_of_stock_parts.exists():
            email_body = "The following parts are out of stock:\n"
            for part in out_of_stock_parts:
                email_body += f"{part.name}\n"
            
            email_data = {
                'email_subject': 'Out-of-Stock Parts Notification',
                'email_body': email_body,
                'to_email': request.user.email  
            }
            Util.send_email(email_data)
            
            return Response({'message': 'Notification sent to staff'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'No out-of-stock parts found'}, status=status.HTTP_200_OK)