from rest_framework import generics, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import exception_handler, APIView

from django.shortcuts import render

from .models import RepairRequest
from .serializers import RepairRequestSerializer, OTPGenerateSerializer, OTPVerifySerializer

from authentication.email import Util
from authentication.models import CustomUser


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

            # Assign the repair request to an available plumber
            plumber = CustomUser.objects.filter(is_available=True).first()

            if plumber:
                repair_request.plumber = plumber
                plumber.is_available = False
                plumber.save()
                repair_request.save()
                # Send confirmation email to the user
                email_data = {
                    'email_subject': 'Repair Request Confirmation',
                    'email_body': f'Thank you for your repair request, {repair_request.name}. We will contact you shortly.',
                    'to_email': repair_request.email,
                }
                Util.send_email(email_data)
                return Response({
                    'message': 'Repair request created successfully. Please check your email for confirmation.',
                    'repair_request_id': repair_request.id
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'No available plumber at the moment. Please try again later.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response


class OTPGenerateAPIView(APIView):
    serializer_class = OTPGenerateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        repair_request = RepairRequest.objects.create(email=email)
        repair_request.generate_otp()
        otp = repair_request.otp

        # Send OTP to user's email
        email_data = {
            'email_subject': 'OTP for Repair Request',
            'email_body': f'Your OTP for the repair request is: {otp}',
            'to_email': email
        }
        Util.send_email(email_data)
        
        return Response({'message': 'OTP generated successfully.'}, status=status.HTTP_200_OK)

class OTPVerifyAPIView(APIView):
    serializer_class = OTPVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            repair_request = RepairRequest.objects.get(email=email, otp=otp, is_completed=False)
            repair_request.otp = None  
            repair_request.otp_created_at = None
            repair_request.is_completed = True
            repair_request.save()

            # Assign the repair request to an available plumber
            plumber = CustomUser.objects.filter(is_available=True).first()

            if plumber:
                repair_request.plumber = plumber
                plumber.is_available = False
                plumber.save()
                repair_request.save()

                # Send confirmation email to the user
                email_data = {
                    'email_subject': 'Repair Request Confirmation',
                    'email_body': f'Thank you for your repair request, {repair_request.name}. We will contact you shortly.',
                    'to_email': repair_request.email,
                }
                Util.send_email(email_data)

                return Response({
                    'message': 'Repair request created successfully. Please check your email for confirmation.',
                    'repair_request_id': repair_request.id
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'No available plumber at the moment. Please try again later.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        except RepairRequest.DoesNotExist:
            return Response({'error': 'Invalid OTP or email.'}, status=status.HTTP_400_BAD_REQUEST)
        

# PLUMBERS APPOINTMENTS API VIEW

class PlumberAppointmentsAPIView(generics.ListAPIView):
    serializer_class = RepairRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RepairRequest.objects.filter(plumber=self.request.user, is_completed=False)