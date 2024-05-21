from datetime import timedelta

from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, smart_str, smart_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from drf_spectacular.utils import extend_schema

from rest_framework import generics, status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .email import Util

from .models import CustomUser
from .serializers import RegistrationSerializer, LoginSerializer, RequestPasswordResetEmailSerializer



# Create your views here.
class RegistrationAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = RegistrationSerializer

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        res = {}

        # Generate verification token
        token = default_token_generator.make_token(user)

        # Store verification token and token creation timestamp in the user model
        user.verification_token = token
        user.token_created_at = timezone.now()
        user.save()

        # Construct verification link
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        verification_link = reverse('verify', kwargs={'uidb64': uidb64, 'token': token})

        # Construct verification URL
        verification_url = f"http://{current_site.domain}{verification_link}"

        # Send verification email to the user
        email_data = {
            'email_subject': 'Account Verification',
            'email_body': f'Please click the link to verify your account: {verification_url}',
            'to_email': user.email
        }
        Util.send_email(email_data)

        res.update(
            {
                'success_message': 'Account created successfully. Please check your email to verify your account',
                'status': status.HTTP_201_CREATED,
                'refresh': user.tokens()['refresh'],
                'access': user.tokens()['access']
            }
        )

        return Response(res, status=status.HTTP_201_CREATED)



@extend_schema(request=None, responses=None)
@api_view(['GET'])
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Check if the token matches the one stored in the user model
        if user.verification_token != token:
            return Response({'error': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token has expired (valid for 5 minutes)
        if user.token_created_at < timezone.now() - timedelta(minutes=5):
            return Response({'error': 'Expired verification link'}, status=status.HTTP_400_BAD_REQUEST)
        

        # Mark the user as active and invalidate the verification token
        user.is_verified = True
        user.verification_token = None
        user.token_created_at = None
        user.save()
        
        return Response({'message': 'Account verified successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)


def resend_verification_email(request, user):
    # Check if the user has recently requested a verification link
    last_request_time = cache.get(f"verification_request:{user.id}")

    if last_request_time:
        # If a request has been made recently, prevent another request within a cooldown period (5 minutes)
        cooldown_period = timedelta(minutes=5)

        if last_request_time + cooldown_period > timezone.now():
            # Return an error or message indicating that the user should wait before making another request
            return None  

    # Generate verification token
    token = default_token_generator.make_token(user)

    # Store verification token and token creation timestamp in the user model
    user.verification_token = token
    user.token_created_at = timezone.now()
    user.save()

    # Construct verification link
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    verification_link = reverse('verify', kwargs={'uidb64': uidb64, 'token': token})

    # Construct verification URL
    verification_url = f"http://{current_site.domain}{verification_link}"

    # Send verification email to the user
    email_data = {
        'email_subject': 'Account Verification',
        'email_body': f'Please click the link to verify your account: {verification_url}',
        'to_email': user.email
    }
    Util.send_email(email_data)

    # Update the last request time in the cache
    cache.set(f"verification_request:{user.id}", timezone.now(), timeout=cooldown_period)

    return verification_url


class LoginAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            # Check if the error message is for user verification
            if 'This user has not been verified' in str(e):
                # If the error is related to user verification, return a custom error message
                return Response({'error': 'This user has not been verified, please check your email for the verification link'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Return other validation errors
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data.get('user')

        if user:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'message': 'Login successful',
                'refresh': str(refresh),
                'access': access_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email')

        if request.data.get('email') is None:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            current_site = get_current_site(request=request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absolute_url = f"http://{current_site}{relative_link}"
            email_body = 'Hello, \n Use the link below to reset password for your account \n' + absolute_url  
            data = {'email_body': email_body, 'to_email': user.email, 'email_subject':'Password Reset'}

            Util.send_email(data)

        
        return Response({'success': 'We have sent a reset link in your email. Please check it out'}, status=status.HTTP_200_OK)