
from rest_framework import serializers
from .models import AirQualityData, EnergyData, OccupancyData

class AirQualityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirQualityData
        fields = '__all__'

class EnergyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyData
        fields = '__all__'

# class RawSensorDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RawSensorData
#         fields = '__all__'

class OccupancyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupancyData
        fields = '__all__'