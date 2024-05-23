import random

from django.db import models
from django.utils import timezone

from authentication.models import CustomUser

# Create your models here.
class RepairRequest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField() 
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    description = models.TextField()
    image = models.ImageField(blank=True, null=True, upload_to='repair_requests/')
    created_at = models.DateTimeField(auto_now_add=True)
    plumber = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)


    def __str__(self):
        return f"Repair Request from {self.name} at {self.address}"
    
    def generate_otp(self):
        self.otp = random.randint(100000, 999999)
        self.otp_created_at = timezone.now()
        self.save()