from datetime import timedelta

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .email import Util

from .models import CustomUser
from .serializers import RegistrationSerializer




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

        # Check if the token has expired (valid for 24 hours)
        if user.token_created_at < timezone.now() - timedelta(days=1):
            return Response({'error': 'Expired verification link'}, status=status.HTTP_400_BAD_REQUEST)
        

        # Mark the user as active and invalidate the verification token
        user.is_verified = True
        user.verification_token = None
        user.token_created_at = None
        user.save()
        
        return Response({'message': 'Account verified successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)
