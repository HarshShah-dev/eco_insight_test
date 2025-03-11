
from rest_framework import serializers
from .models import SensorData, EMData, RawSensorData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = '__all__'

class EMDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMData
        fields = '__all__'

class RawSensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawSensorData
        fields = '__all__'