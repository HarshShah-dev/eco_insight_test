
from rest_framework import serializers
from .models import SensorData, EMData, RawSensorData, ParsedSensorData

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

class ParsedSensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedSensorData
        fields = '__all__'