from django.db import models

# Create your models here.
class RepairRequest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField() 
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    description = models.TextField()
    image = models.ImageField(blank=True, null=True, upload_to='repair_requests/')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Repair Request from {self.name} at {self.address}"