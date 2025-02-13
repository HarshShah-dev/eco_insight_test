from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .models import SensorData, EMData
from .serializers import SensorDataSerializer, EMDataSerializer

# class SensorReadingCreateView(APIView):
#     # Allow all clients (no authentication needed)
#     permission_classes = [AllowAny]
#     authentication_classes = []

#     def post(self, request, format=None):
#         serializer = SensorReadingSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()  # Save the sensor reading to the database
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SensorDataListView(APIView):
    def get(self, request, format=None):
        # For example, get the most recent sensor reading
        latest_data = SensorData.objects.order_by('-timestamp').first()
        if latest_data:
            serializer = SensorDataSerializer(latest_data)
            return Response(serializer.data)
        else:
            return Response({"detail": "No sensor data available."})
        
class EMDataListView(APIView):
    def get(self, request, format=None):
        # For example, get the most recent EM data entry
        latest_data = EMData.objects.order_by('-timestamp').first()
        if latest_data:
            serializer = EMDataSerializer(latest_data)
            return Response(serializer.data)
        else:
            return Response({"detail": "No EM data available."})