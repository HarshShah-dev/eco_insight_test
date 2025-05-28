from django.contrib import admin
from .models import AirQualityData, EnergyData, OccupancyData
# Register your models here.
admin.site.register(AirQualityData)
admin.site.register(EnergyData)
admin.site.register(OccupancyData)