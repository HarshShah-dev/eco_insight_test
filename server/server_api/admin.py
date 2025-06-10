from django.contrib import admin
from .models import Sensor, AirQualityData, EnergyData, OccupancyData, RadarData

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'sensor_type', 'floor', 'office', 'active')
    list_filter = ('sensor_type', 'floor', 'active')
    search_fields = ('sensor_id', 'office', 'description')

@admin.register(AirQualityData)
class AirQualityDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'device', 'co2', 'temp', 'humidity', 'timestamp')
    list_filter = ('sensor', 'timestamp')
    search_fields = ('device', 'sensor__sensor_id')

@admin.register(EnergyData)
class EnergyDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'device_id', 'total_current', 'total_act_power', 'timestamp')
    list_filter = ('sensor', 'timestamp')
    search_fields = ('device_id', 'sensor__sensor_id')

@admin.register(OccupancyData)
class OccupancyDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'mac', 'entries', 'exits', 'total_entries', 'total_exits', 'timestamp')
    list_filter = ('sensor', 'timestamp')
    search_fields = ('mac', 'sensor__sensor_id')

@admin.register(RadarData)
class RadarDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'mac', 'num_targets', 'timestamp')
    list_filter = ('sensor', 'timestamp')
    search_fields = ('mac', 'sensor__sensor_id')