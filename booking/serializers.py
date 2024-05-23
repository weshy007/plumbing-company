from rest_framework import serializers

from .models import RepairRequest


class RepairRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairRequest
        fields = ['name', 'email', 'phone_number', 'address', 'description', 'image']
        read_only_fields = ['created_at']
        extra_kwargs = {'otp': {'write_only': True}}

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must be a number")
        if len(value) not in [10, 11]:
            raise serializers.ValidationError("Phone number must be 10 or 11 digits.")
        return value
    
    def validate_email(self, value):
        if '@' not in value:
            raise serializers.ValidationError("Invalid email address.")
        return value
    

class OTPGenerateSerializer(serializers.Serializer):
    email = serializers.EmailField()

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)