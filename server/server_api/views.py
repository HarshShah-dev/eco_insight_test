from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .models import AirQualityData, EnergyData, OccupancyData, Sensor, RadarData, SensorData
from .serializers import AirQualityDataSerializer, EnergyDataSerializer, OccupancyDataSerializer, RadarDataSerializer, SensorSerializer, SensorDataSerializer
from dateutil import parser as dateparser
from .utils import parse_minew_data
from django.utils import timezone
from django.shortcuts import get_object_or_404

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

def get_or_create_sensor(sensor_id, sensor_type, mac=None):
    """Helper function to get or create a sensor"""
    try:
        sensor = Sensor.objects.get(sensor_id=sensor_id)
        return sensor
    except Sensor.DoesNotExist:
        # Create new sensor if it doesn't exist
        sensor = Sensor.objects.create(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            description=f"Auto-created {sensor_type} sensor"
        )
        return sensor

class AirQualityDataListView(APIView):
    def get(self, request, format=None):
        latest_data = AirQualityData.objects.order_by('-timestamp').first()
        if latest_data:
            serializer = AirQualityDataSerializer(latest_data)
            return Response(serializer.data)
        else:
            return Response({"detail": "No sensor data available."})

    def post(self, request, format=None):
        data = request.data.copy()
        sensor_id = data.get('device')  # Using device field as sensor_id
        sensor = get_or_create_sensor(sensor_id, 'AQ')
        data['sensor_id'] = sensor.id
        
        serializer = AirQualityDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnergyDataListView(APIView):
    def get(self, request, format=None):
        latest_data = EnergyData.objects.order_by('-timestamp').first()
        if latest_data:
            serializer = EnergyDataSerializer(latest_data)
            return Response(serializer.data)
        else:
            return Response({"detail": "No Energy data available."})

    def post(self, request, format=None):
        data = request.data.copy()
        sensor_id = str(data.get('device_id'))  # Using device_id as sensor_id
        sensor = get_or_create_sensor(sensor_id, 'EM')
        data['sensor_id'] = sensor.id
        
        serializer = EnergyDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        sensor_data_list = request.data
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

        last_record = OccupancyData.objects.order_by('-created_at').first()
        if last_record:
            i_total_entries = last_record.total_entries
            i_total_exits = last_record.total_exits
            i_s_no = last_record.serial_number
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
            i_total_entries += entries
            i_total_exits += exits

        # Get or create sensor
        sensor = get_or_create_sensor(mac, 'OC')

        # Create a new OccupancyData record combining sensor JSON and parsed info
        record = OccupancyData.objects.create(
            sensor=sensor,
            mac=parsed_dict.get("mac") or mac,
            frame_version=parsed_dict.get("frame_version"),
            battery=parsed_dict.get("battery"),
            firmware_version=parsed_dict.get("firmware_version"),
            peripheral_support=parsed_dict.get("peripheral_support"),
            salt=parsed_dict.get("salt"),
            digital_signature=parsed_dict.get("digital_signature"),
            usage=parsed_dict.get("usage"),
            serial_number=parsed_dict.get("serial_number"),
            entries=parsed_dict.get("entries"),
            exits=parsed_dict.get("exits"),
            random_number=parsed_dict.get("random_number"),
            raw_data=parsed_dict.get("raw") or raw,
            rssi=parsed_dict.get("rssi") or rssi,
            timestamp=timestamp_1,
            total_entries=i_total_entries,
            total_exits=i_total_exits,
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
        data = AirQualityData.objects.order_by('-timestamp')[::100]  # last 100 entries
        return Response(AirQualityDataSerializer(data, many=True).data)

class EnergyDataHistoryView(APIView):
    def get(self, request):
        data = EnergyData.objects.order_by('-timestamp')[::100]
        return Response(EnergyDataSerializer(data, many=True).data)

class OccupancyDataHistoryView(APIView):
    def get(self, request):
        data = OccupancyData.objects.order_by('-timestamp')[::100]
        return Response(OccupancyDataSerializer(data, many=True).data)
    
class EnergyDataHistoryViewLevel3(APIView):
    def get(self, request):
        sensor = get_object_or_404(Sensor, sensor_id='0', sensor_type='EM')
        data = EnergyData.objects.filter(sensor=sensor).order_by('-timestamp')[::100]
        return Response(EnergyDataSerializer(data, many=True).data)

class EnergyDataHistoryViewLevel4(APIView):
    def get(self, request):
        sensor = get_object_or_404(Sensor, sensor_id='1', sensor_type='EM')
        data = EnergyData.objects.filter(sensor=sensor).order_by('-timestamp')[::100]
        return Response(EnergyDataSerializer(data, many=True).data)



class RadarDataCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            radar_info = data.get("radar", {})
            coordinates = radar_info.get("coord", {})
            mac = data.get("mac")
            
            # Get or create sensor
            sensor = get_or_create_sensor(mac, 'RD', mac=mac)
            
            record = RadarData.objects.create(
                sensor=sensor,
                mac=mac,
                sn=int(data.get("sn")),
                timestamp=data.get("timestamp"),
                num_targets=int(radar_info.get("num", 0)),
                coordinates=coordinates,
                raw_payload=data
            )
            return Response({"status": "created", "id": record.id}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class SensorListView(APIView):
    def get(self, request):
        sensors = Sensor.objects.all()
        return Response(SensorSerializer(sensors, many=True).data)

    def post(self, request):
        serializer = SensorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SensorDetailView(APIView):
    def get(self, request, sensor_id):
        sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
        return Response(SensorSerializer(sensor).data)

    def put(self, request, sensor_id):
        sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
        serializer = SensorSerializer(sensor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, sensor_id):
        sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
        sensor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SensorDataListView(APIView):
    def get(self, request):
        data = SensorData.objects.order_by('-timestamp')[:100]  # last 100 entries
        return Response(SensorDataSerializer(data, many=True).data)

    def post(self, request):
        serializer = SensorDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SensorDataHistoryView(APIView):
    def get(self, request, sensor_id):
        sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
        data = SensorData.objects.filter(sensor=sensor).order_by('-timestamp')[:100]
        return Response(SensorDataSerializer(data, many=True).data)

class SensorDataByActionView(APIView):
    def get(self, request, action):
        data = SensorData.objects.filter(action=action).order_by('-timestamp')[:100]
        return Response(SensorDataSerializer(data, many=True).data)