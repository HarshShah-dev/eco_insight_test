
from rest_framework import serializers
from .models import SensorData, EMData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = '__all__'

class EMDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMData
        fields = '__all__'