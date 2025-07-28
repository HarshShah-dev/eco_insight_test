from django.contrib import admin
from .models import (
    Sensor, AirQualityData, EnergyData, OccupancyData, 
    RadarData, SensorData, RawSensorData, TemperatureHumidityData, Lsg01AirQualityData,
    WeatherLocation, WeatherHourly, WeatherDaily, WeatherCurrent
)


@admin.register(Lsg01AirQualityData)
class LSG01AirQualityDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'sensor', 'temperature', 'humidity', 'pm25', 'hcho', 'co2', 'tvoc', 'timestamp')
    list_filter = ("device", "timestamp")
    search_fields = ("device", "sensor__sensor_id")

@admin.register(TemperatureHumidityData)
class TemperatureHumidityDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'device', 'temperature', 'humidity', 'timestamp')
    list_filter = ('sensor', 'timestamp')
    search_fields = ('device', 'sensor__sensor_id')

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

@admin.register(RawSensorData)
class RawSensorDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'received_at', 'short_preview')
    readonly_fields = ('raw_data', 'received_at')
    search_fields = ('raw_data',)
    ordering = ('-received_at',)

    def short_preview(self, obj):
        return str(obj.raw_data)[:75] + "..." if len(str(obj.raw_data)) > 75 else str(obj.raw_data)
    short_preview.short_description = "Raw Data Preview"

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'action', 'device_id', 'mac')
    list_filter = ('sensor__sensor_type', 'action', 'timestamp')
    search_fields = ('sensor__sensor_id', 'device_id', 'mac', 'action')
    readonly_fields = ('action',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('sensor', 'timestamp', 'action', 'device_id', 'mac')
        }),
        ('Air Quality Data', {
            'fields': ('quality', 'co2', 'temp', 'humidity', 'voc', 'pm2p5', 'pm10', 'pm1', 'pm4', 'version'),
            'classes': ('collapse',)
        }),
        ('Energy Meter Data', {
            'fields': (
                'a_current', 'a_voltage', 'a_act_power', 'a_aprt_power', 'a_pf', 'a_freq',
                'b_current', 'b_voltage', 'b_act_power', 'b_aprt_power', 'b_pf', 'b_freq',
                'c_current', 'c_voltage', 'c_act_power', 'c_aprt_power', 'c_pf', 'c_freq',
                'total_current', 'total_act_power', 'total_aprt_power'
            ),
            'classes': ('collapse',)
        }),
        ('Occupancy Data', {
            'fields': ('frame_version', 'serial_number', 'entries', 'exits', 'total_entries', 'total_exits'),
            'classes': ('collapse',)
        }),
        ('Radar Data', {
            'fields': ('sn', 'num_targets', 'coordinates', 'raw_payload'),
            'classes': ('collapse',)
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.fieldsets
        
        # Show only relevant fieldsets based on sensor type
        fieldsets = [self.fieldsets[0]]  # Always show basic information
        
        if obj.sensor.sensor_type == 'AQ':
            fieldsets.append(self.fieldsets[1])
        elif obj.sensor.sensor_type == 'EM':
            fieldsets.append(self.fieldsets[2])
        elif obj.sensor.sensor_type == 'OC':
            fieldsets.append(self.fieldsets[3])
        elif obj.sensor.sensor_type == 'RD':
            fieldsets.append(self.fieldsets[4])
            
        return fieldsets



@admin.register(WeatherLocation)
class WeatherLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "timezone", "active")
    list_filter = ("active", "timezone")
    search_fields = ("name",)


@admin.register(WeatherHourly)
class WeatherHourlyAdmin(admin.ModelAdmin):
    list_display = ("location", "time", "temperature_2m", "apparent_temperature", "precipitation_probability", "weather_code")
    list_filter = ("location", "time")
    search_fields = ("location__name",)


@admin.register(WeatherDaily)
class WeatherDailyAdmin(admin.ModelAdmin):
    list_display = ("location", "date", "temperature_2m_min", "temperature_2m_max", "precipitation_probability_max", "weather_code")
    list_filter = ("location", "date")
    search_fields = ("location__name",)


@admin.register(WeatherCurrent)
class WeatherCurrentAdmin(admin.ModelAdmin):
    list_display = ("location", "observed_at", "temperature_2m", "apparent_temperature", "precipitation", "weather_code")
    list_filter = ("location", "observed_at")
    search_fields = ("location__name",)
