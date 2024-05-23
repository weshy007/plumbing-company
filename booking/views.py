from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import exception_handler

from django.shortcuts import render

from .models import RepairRequest
from .serializers import RepairRequestSerializer

from authentication.email import Util


class BurstRateThrottle(UserRateThrottle):
    rate = '5/minute'


# Create your views here.
class RepairRequestCreateAPIView(generics.CreateAPIView):
    queryset = RepairRequest.objects.all()
    serializer_class = RepairRequestSerializer
    throttle_classes = [BurstRateThrottle]

    def perform_create(self, serializer):
        try:
            repair_request = serializer.save()

            # Send confirmation email
            email_data = {
                'email_subject': 'Repair Request Confirmation',
                'email_body': f'Thank you for your repair request, {repair_request.name}. We will contact you shortly.',
                'to_email': repair_request.email,
            }

            Util.send_email(email_data)
    
            return Response({
                'message': 'Repair request created successfully. Please check your email for confirmation.',
                'repair_request_id': repair_request.id
            }), status.HTTP_201_CREATED
        
        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response