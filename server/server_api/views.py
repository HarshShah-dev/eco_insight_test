from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .models import AirQualityData, EnergyData, OccupancyData, Sensor
from .serializers import AirQualityDataSerializer, EnergyDataSerializer, OccupancyDataSerializer
from dateutil import parser as dateparser
from .utils import parse_minew_data
from django.utils import timezone

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

class AirQualityDataListView(APIView):
    def get(self, request, format=None):
        # For example, get the most recent AQ sensor reading
        latest_data = AirQualityData.objects.order_by('-timestamp').first()
        if latest_data:
            serializer = AirQualityDataSerializer(latest_data)
            return Response(serializer.data)
        else:
            return Response({"detail": "No sensor data available."})

class EnergyDataListView(APIView):
    def get(self, request, format=None):
        # For example, get the most recent Energy data entry
        latest_data = EnergyData.objects.order_by('-timestamp').first()
        if latest_data:
            serializer = EnergyDataSerializer(latest_data)
            return Response(serializer.data)
        else:
            return Response({"detail": "No Energy data available."})

# class RawSensorDataCreateView(APIView):
#     # Allow all requests without authentication
#     permission_classes = [AllowAny]

#     def post(self, request, format=None):
#         # Wrap the incoming JSON data into a dict with key 'raw_data'
#         serializer = RawSensorDataSerializer(data={'raw_data': request.data})
#         if serializer.is_valid():
#             serializer.save()  # Save the raw data to the database
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# server_api/views.py


class OccupancyDataCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        sensor_data_list = request.data  # Expecting a JSON array
        created_count = 0
        errors = []
        i_total_entries = 0
        i_total_exits = 0
        parsed_dict = {}
        rssi = -1
        mac = 123
        # timestamp_str = "2025-03-25T06:02:57.717Z"
        s_no = 0
        i_s_no = 0

        # Get cumulative totals from the latest record in the database (if any)
        last_record = OccupancyData.objects.order_by('-created_at').first()
        if last_record:
            i_total_entries = last_record.total_entries
            i_total_exits = last_record.total_exits
            i_s_no = last_record.serial_number
            print(i_s_no)
        else:
            i_total_entries = 0
            i_total_exits = 0
            i_s_no = 0

        for item in sensor_data_list:
            # Skip gateway records
            if "gateway" in item:
                continue

            if "raw" in item:
                raw = item.get("raw")
                parsed_dict.update(parse_minew_data(raw))
                # You may choose to log or handle errors if "error" key exists.
                # For this example, we continue only if no error.
                if parsed_dict.get("error"):
                    errors.append(f"Error parsing raw data for item {item}: {parsed_dict.get('error')}")
                    continue
            else:
                errors.append(f"Missing 'raw' field in item: {item}")
                continue
            
            mac = item.get("mac")
            rssi = item.get("rssi")
            timestamp_1 = timezone.now()  # Default to current time if not provided
            # try:
            #     timestamp = dateparser.parse(timestamp_str)
            # except Exception:
            #     errors.append(f"Invalid timestamp: {timestamp_str}")
            #     continue
        timestamp_1 = timezone.now()

        # Get the number of new entries and exits from the parsed data.
        s_no = int(parsed_dict.get("serial_number", 0))
        print(s_no)
        entries = int(parsed_dict.get("entries", 0))
        exits = int(parsed_dict.get("exits", 0))
        
        
        if s_no != i_s_no:
        # Update cumulative totals
            i_total_entries += entries
            i_total_exits += exits
        # i_total_entries += int(parsed_dict.get("entries", 0))
        # i_total_exits += int(parsed_dict.get("exits", 0))

        sensor = Sensor.objects.get(sensor_id=parsed_dict.get("mac") or mac)

        # Create a new OccupancyData record combining sensor JSON and parsed info
        record = OccupancyData.objects.create(
            sensor = sensor,
            mac = parsed_dict.get("mac") or mac,
            frame_version = parsed_dict.get("frame_version"),
            battery = parsed_dict.get("battery"),
            firmware_version = parsed_dict.get("firmware_version"),
            peripheral_support = parsed_dict.get("peripheral_support"),
            salt = parsed_dict.get("salt"),
            digital_signature = parsed_dict.get("digital_signature"),
            usage = parsed_dict.get("usage"),
            serial_number = parsed_dict.get("serial_number"),
            # entries = total_entries + parsed_dict.get("entries"),
            # exits = total_exits + parsed_dict.get("exits"),
            entries = parsed_dict.get("entries"),
            exits = parsed_dict.get("exits"),
            random_number = parsed_dict.get("random_number"),
            raw_data = parsed_dict.get("raw") or raw,
            rssi = parsed_dict.get("rssi") or rssi,
            timestamp = timestamp_1,
            total_entries = i_total_entries,
            total_exits = i_total_exits,
        )
        
        print(f"Created record: {record.id}")
        created_count += 1
        parsed_dict = {}  # Reset parsed data for next iteration


        print(f"Total entries processed: {i_total_entries}, Total exits processed: {i_total_exits}")

        if errors:
            return Response({"errors": errors, "created": created_count}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"created": created_count}, status=status.HTTP_201_CREATED)


class AirQualityDataHistoryView(APIView):
    def get(self, request):
        data = AirQualityData.objects.order_by('-timestamp')[:100]  # last 100 entries
        return Response(AirQualityDataSerializer(data, many=True).data)

class EnergyDataHistoryView(APIView):
    def get(self, request):
        data = EnergyData.objects.order_by('-timestamp')[:100]
        return Response(EnergyDataSerializer(data, many=True).data)

class OccupancyDataHistoryView(APIView):
    def get(self, request):
        data = OccupancyData.objects.order_by('-timestamp')[:100]
        return Response(OccupancyDataSerializer(data, many=True).data)
    
class EnergyDataHistoryViewLevel3(APIView):
    def get(self, request):
        data = EnergyData.objects.filter(device_id=0).order_by('-timestamp')[:100]
        return Response(EnergyDataSerializer(data, many=True).data)

class EnergyDataHistoryViewLevel4(APIView):
    def get(self, request):
        data = EnergyData.objects.filter(device_id=1).order_by('-timestamp')[:100]
        return Response(EnergyDataSerializer(data, many=True).data)