from django.db import models

from booking.models import Parts

# Create your models here.
class RestockPart(models.Model):
    part = models.ForeignKey(Parts, on_delete=models.CASCADE)
    required_quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.part.name} needs restock'
    

