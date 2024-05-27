from rest_framework import serializers

from .models import RestockPart

class RestockPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestockPart
        fields = ['part', 'required_quantity', 'added_at']