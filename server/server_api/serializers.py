from rest_framework import serializers
from .models import AirQualityData, EnergyData, OccupancyData, RadarData, Sensor, SensorData, RawSensorData, TemperatureHumidityData, LSG01AirQualityData


class LSG01AirQualityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LSG01AirQualityData
        fields = "__all__"



class TemperatureHumidityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureHumidityData
        fields = '__all__'

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'sensor_id', 'sensor_type', 'floor', 'office', 'description', 'active']

class AirQualityDataSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.filter(sensor_type='AQ'),
        source='sensor',
        write_only=True
    )

    class Meta:
        model = AirQualityData
        fields = '__all__'

class EnergyDataSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.filter(sensor_type='EM'),
        source='sensor',
        write_only=True
    )

    class Meta:
        model = EnergyData
        fields = '__all__'

class RawSensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawSensorData
        fields = '__all__'

class OccupancyDataSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.filter(sensor_type='OC'),
        source='sensor',
        write_only=True
    )

    class Meta:
        model = OccupancyData
        fields = '__all__'

class RadarDataSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.filter(sensor_type='RD'),
        source='sensor',
        write_only=True
    )

    class Meta:
        model = RadarData
        fields = '__all__'

class SensorDataSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.all(),
        source='sensor',
        write_only=True
    )

    class Meta:
        model = SensorData
        fields = '__all__'