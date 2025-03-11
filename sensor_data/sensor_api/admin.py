from django.contrib import admin
from .models import SensorData, EMData, RawSensorData
# Register your models here.
admin.site.register(SensorData)
admin.site.register(EMData)
admin.site.register(RawSensorData)
