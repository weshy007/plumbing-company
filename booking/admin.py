from django.contrib import admin

from .models import RepairRequest, Parts

# Register your models here.
admin.site.register(RepairRequest)
admin.site.register(Parts)