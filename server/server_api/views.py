from django.shortcuts import render
from collections import defaultdict
from datetime import datetime
import pytz
import time
import logging
logger = logging.getLogger(__name__)
from .utils import parse_mst01_ht_payload
import base64
import traceback
from .utils import get_energy_summary, build_input_vector_from_latest_data, generate_recommendations_by_location, parse_lsg01_payload_dynamically
# Create your views here.
import joblib
from rest_framework.decorators import api_view

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .models import AirQualityData, EnergyData, OccupancyData, Sensor, RadarData, SensorData, Lsg01AirQualityData
from .serializers import Lsg01AirQualityDataSerializer, AirQualityDataSerializer, TemperatureHumidityDataSerializer, EnergyDataSerializer, OccupancyDataSerializer, RadarDataSerializer, SensorSerializer, SensorDataSerializer, RawSensorDataSerializer
from dateutil import parser as dateparser
from .utils import parse_minew_data, parse_lsg01_payload, parse_mst01_ht_payload
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .ml_model_loader import forecast_models, recommendation_model, label_encoder
import pandas as pd
import numpy as np
from django.utils.timezone import now
from itertools import chain

# views.py (partial)




# class LSG01AQPushView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         try:
#             data = request.data
#             device_id = data.get("end_device_ids", {}).get("device_id")
#             dev_eui = data.get("end_device_ids", {}).get("dev_eui")
#             payload_b64 = data.get("uplink_message", {}).get("frm_payload")
#             timestamp_str = data.get("received_at")

#             if not all([device_id, dev_eui, payload_b64, timestamp_str]):
#                 return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

#             raw_bytes = base64.b64decode(payload_b64)

#             # Parse data
#             co2 = int.from_bytes(raw_bytes[0:2], 'big')
#             temp_raw = int.from_bytes(raw_bytes[2:4], 'big')
#             temp = temp_raw / 10.0
#             humidity = raw_bytes[4]
#             pm2p5 = int.from_bytes(raw_bytes[5:7], 'big')
#             pm10 = int.from_bytes(raw_bytes[7:9], 'big')
#             tvoc_index = int.from_bytes(raw_bytes[9:11], 'big')

#             # Timestamp
#             timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

#             # Get or create sensor
#             sensor = get_or_create_sensor(device_id, 'AQ')

#             record = {
#                 "sensor_id": sensor.id,
#                 "device": device_id,
#                 "co2": co2,
#                 "temp": temp,
#                 "humidity": humidity,
#                 "pm2p5": pm2p5,
#                 "pm10": pm10,
#                 "voc": tvoc_index,
#                 "timestamp": timestamp,
#                 "version": "LSG01",
#                 "quality": "Unknown",
#             }

#             serializer = LSG01AirQualityDataSerializer(data=record)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Lsg01DataPush(APIView):
    def post(self, request):
        print("[DEBUG] Received LSG01 payload:", request.data)
        try:
            payload = request.data
            logger.debug(f"Incoming payload: {payload}")

            device_id = payload["end_device_ids"]["device_id"]
            frm_payload = payload["uplink_message"]["frm_payload"]

            # Decode sensor readings
            parsed_data = parse_lsg01_payload_dynamically(frm_payload)
            logger.debug(f"Parsed data: {parsed_data}")

            if "error" in parsed_data:
                return Response({"error": parsed_data["error"]}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create sensor (optional - modify if needed)
            sensor = Sensor.objects.filter(sensor_id=device_id).first()
            if not sensor:
                return Response({"error": f"Sensor {device_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

            parsed_data["sensor"] = sensor.id
            parsed_data["device"] = device_id

            serializer = Lsg01AirQualityDataSerializer(data=parsed_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Error processing LSG01 data.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemperatureHumidityCreateView(APIView):
    def post(self, request):
        frm_payload = request.data.get("data", {}).get("uplink_message", {}).get("frm_payload")
        dev_id = request.data.get("data", {}).get("end_device_ids", {}).get("device_id", "unknown")

        if not frm_payload:
            return Response({"error": "Missing frm_payload"}, status=status.HTTP_400_BAD_REQUEST)

        parsed = parse_mst01_ht_payload(frm_payload)
        if "error" in parsed:
            return Response(parsed, status=status.HTTP_400_BAD_REQUEST)

        # Get or create sensor
        sensor = Sensor.objects.filter(sensor_id=dev_id).first()
        if not sensor:
            sensor = Sensor.objects.create(sensor_id=dev_id, sensor_type='AQ', description="MST01 Temp/Humidity Sensor")

        data = {
            "sensor_id": sensor.id,
            "device": dev_id,
            "co2": 0,
            "temp": int(parsed["temperature"]),
            "humidity": int(parsed["humidity"]),
            "voc": 0,
            "pm2p5": 0.0,
            "pm10": 0.0,
            "pm1": 0.0,
            "pm4": 0.0,
            "timestamp": now(),
            "quality": "Unknown",
            "version": "MST01",
        }

        serializer = AirQualityDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class TemperatureHumidityCreateView(APIView):
#     def post(self, request):
#         payload = request.data
#         device_id = payload.get("end_device_ids", {}).get("device_id")
#         frm_payload = payload.get("uplink_message", {}).get("frm_payload")

#         if not device_id or not frm_payload:
#             return Response({"error": "Missing device_id or frm_payload"}, status=400)

#         parsed = parse_mst01_ht_payload(frm_payload)
#         if "error" in parsed:
#             return Response(parsed, status=400)

#         # Get or create sensor
#         sensor = Sensor.objects.filter(sensor_id=device_id).first()
#         if not sensor:
#             sensor = Sensor.objects.create(sensor_id=device_id, sensor_type='AQ', description="MST01 Sensor")

#         data = {
#             "sensor": sensor.id,
#             "device": device_id,
#             "temperature": parsed["temperature"],
#             "humidity": parsed["humidity"],
#         }

#         serializer = TemperatureHumidityDataSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         print("[DEBUG] Serializer errors:", serializer.errors)
#         return Response({"errors": serializer.errors}, status=400)
# class TemperatureHumidityCreateView(APIView):
#     def post(self, request):
#         try:
#             payload = request.data
#             print("[DEBUG] Incoming payload:", payload)

#             device_id = payload.get("end_device_ids", {}).get("device_id")
#             frm_payload = payload.get("uplink_message", {}).get("frm_payload")

#             if not device_id or not frm_payload:
#                 return Response({"error": "Missing device_id or frm_payload"}, status=400)

#             parsed = parse_mst01_ht_payload(frm_payload)
#             print("[DEBUG] Decoded values:", parsed)

#             if "error" in parsed:
#                 return Response(parsed, status=400)

#             sensor = Sensor.objects.filter(sensor_id=device_id).first()
#             if not sensor:
#                 sensor = Sensor.objects.create(sensor_id=device_id, sensor_type='AQ', description="MST01 Sensor")

#             data = {
#                 "sensor": sensor.id,
#                 "device": device_id,
#                 "temperature": parsed["temperature"],
#                 "humidity": parsed["humidity"],
#             }

#             print("[DEBUG] Data sent to serializer:", data)
#             serializer = TemperatureHumidityDataSerializer(data=data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=201)
#             else:
#                 print("[DEBUG] Serializer errors:", serializer.errors)
#                 return Response({"errors": serializer.errors}, status=400)

#         except Exception as e:
#             print("[ERROR]", str(e))
#             return Response({"error": str(e)}, status=500)


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

# class AirQualityDataListView(APIView):
#     def get(self, request, format=None):
#         latest_data = AirQualityData.objects.order_by('-timestamp').first()
#         if latest_data:
#             serializer = AirQualityDataSerializer(latest_data)
#             return Response(serializer.data)
#         else:
#             return Response({"detail": "No sensor data available."})

#     def post(self, request, format=None):
#         data = request.data.copy()
#         sensor_id = data.get('device')  # Using device field as sensor_id
#         sensor = get_or_create_sensor(sensor_id, 'AQ')
#         data['sensor_id'] = sensor.id
        
#         serializer = AirQualityDataSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AirQualitySensorPushView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            payload = request.data.get("msg", {})
            if not payload:
                return Response({"error": "Missing 'msg' field"}, status=status.HTTP_400_BAD_REQUEST)

            device_id = payload.get("device_id")
            if not device_id:
                return Response({"error": "Missing 'device_id'"}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create sensor
            sensor = get_or_create_sensor(device_id, 'AQ')

            # Convert UNIX timestamp to timezone-aware datetime
            ts = int(payload.get("timestamp", time.time()))
            timestamp = datetime.fromtimestamp(ts, tz=pytz.UTC)

            aq_data = {
                "sensor_id": sensor.id,
                "device": device_id,
                "co2": int(payload.get("co2", 0)),
                "temp": int(payload.get("temperature", 0)),
                "humidity": int(payload.get("humidity", 0)),
                "voc": int(payload.get("tvoc_index", 0)),
                "pm2p5": float(payload.get("pm_2p5", 0.0)),
                "pm10": float(payload.get("pm_10", 0.0)),
                "pm1": float(payload.get("pm_1", 0.0)),
                "pm4": float(payload.get("pm_4", 0.0)),
                "timestamp": timestamp,
                "quality": "Unknown",
                "version": payload.get("company_name", "Unknown"),
            }

            serializer = AirQualityDataSerializer(data=aq_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class RawSensorDataCreateView(APIView):
    # Allow all requests without authentication
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        # Wrap the incoming JSON data into a dict with key 'raw_data'
        serializer = RawSensorDataSerializer(data={'raw_data': request.data})
        if serializer.is_valid():
            serializer.save()  # Save the raw data to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# server_api/views.py


# class OccupancyDataCreateView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, format=None):
#         sensor_data_list = request.data
#         created_count = 0
#         errors = []
#         i_total_entries = 0
#         i_total_exits = 0
#         parsed_dict = {}
#         rssi = -1
#         mac = 123
#         # timestamp_str = "2025-03-25T06:02:57.717Z"
#         s_no = 0
#         i_s_no = 0

#         last_record = OccupancyData.objects.order_by('-created_at').first()
#         if last_record:
#             i_total_entries = last_record.total_entries
#             i_total_exits = last_record.total_exits
#             i_s_no = last_record.serial_number
#         else:
#             i_total_entries = 0
#             i_total_exits = 0
#             i_s_no = 0

#         for item in sensor_data_list:
#             # Skip gateway records
#             if "gateway" in item:
#                 continue

#             if "raw" in item:
#                 raw = item.get("raw")
#                 parsed_dict.update(parse_minew_data(raw))
#                 # You may choose to log or handle errors if "error" key exists.
#                 # For this example, we continue only if no error.
#                 if parsed_dict.get("error"):
#                     errors.append(f"Error parsing raw data for item {item}: {parsed_dict.get('error')}")
#                     continue
#             else:
#                 errors.append(f"Missing 'raw' field in item: {item}")
#                 continue
            
#             mac = item.get("mac")
#             rssi = item.get("rssi")
#             timestamp_1 = timezone.now()  # Default to current time if not provided
#             # try:
#             #     timestamp = dateparser.parse(timestamp_str)
#             # except Exception:
#             #     errors.append(f"Invalid timestamp: {timestamp_str}")
#             #     continue
#         timestamp_1 = timezone.now()

#         # Get the number of new entries and exits from the parsed data.
#         s_no = int(parsed_dict.get("serial_number", 0))
#         print(s_no)
#         entries = int(parsed_dict.get("entries", 0))
#         exits = int(parsed_dict.get("exits", 0))
        
        
#         if s_no != i_s_no:
#             i_total_entries += entries
#             i_total_exits += exits

#         # Get or create sensor
#         sensor = get_or_create_sensor(mac, 'OC')

#         # Create a new OccupancyData record combining sensor JSON and parsed info
#         record = OccupancyData.objects.create(
#             sensor=sensor,
#             mac=parsed_dict.get("mac") or mac,
#             frame_version=parsed_dict.get("frame_version"),
#             battery=parsed_dict.get("battery"),
#             firmware_version=parsed_dict.get("firmware_version"),
#             peripheral_support=parsed_dict.get("peripheral_support"),
#             salt=parsed_dict.get("salt"),
#             digital_signature=parsed_dict.get("digital_signature"),
#             usage=parsed_dict.get("usage"),
#             serial_number=parsed_dict.get("serial_number"),
#             entries=parsed_dict.get("entries"),
#             exits=parsed_dict.get("exits"),
#             random_number=parsed_dict.get("random_number"),
#             raw_data=parsed_dict.get("raw") or raw,
#             rssi=parsed_dict.get("rssi") or rssi,
#             timestamp=timestamp_1,
#             total_entries=i_total_entries,
#             total_exits=i_total_exits,
#         )
        
#         print(f"Created record: {record.id}")
#         created_count += 1
#         parsed_dict = {}  # Reset parsed data for next iteration


#         print(f"Total entries processed: {i_total_entries}, Total exits processed: {i_total_exits}")

#         if errors:
#             return Response({"errors": errors, "created": created_count}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"created": created_count}, status=status.HTTP_201_CREATED)

class OccupancyDataCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        sensor_data_list = request.data
        created_count = 0
        errors = []
        totals_by_sensor = defaultdict(lambda: {"entries": 0, "exits": 0, "s_no": 0})

        for item in sensor_data_list:
            if "gateway" in item or "raw" not in item:
                continue

            raw = item["raw"]
            parsed_dict = parse_minew_data(raw)

            # Skip device information frame (frame_version == "00")
            if parsed_dict.get("frame_version") == "00":
                continue

            # Skip if any other error
            if parsed_dict.get("error"):
                errors.append(f"Error parsing raw data for item {item}: {parsed_dict.get('error')}")
                continue


            mac = item.get("mac", parsed_dict.get("mac", "unknown-mac"))
            rssi = item.get("rssi", -99)
            timestamp = timezone.now()
            serial_no = int(parsed_dict.get("serial_number", 0))
            entries = int(parsed_dict.get("entries", 0))
            exits = int(parsed_dict.get("exits", 0))

            # Get or create sensor per MAC
            sensor = get_or_create_sensor(mac, 'OC')

            # Get last known totals for this sensor
            if mac not in totals_by_sensor:
                last_record = OccupancyData.objects.filter(sensor=sensor).order_by('-created_at').first()
                totals_by_sensor[mac]["entries"] = last_record.total_entries if last_record else 0
                totals_by_sensor[mac]["exits"] = last_record.total_exits if last_record else 0
                totals_by_sensor[mac]["s_no"] = last_record.serial_number if last_record else -1

            if serial_no != totals_by_sensor[mac]["s_no"]:
                totals_by_sensor[mac]["entries"] += entries
                totals_by_sensor[mac]["exits"] += exits
                totals_by_sensor[mac]["s_no"] = serial_no

            # Save record
            record = OccupancyData.objects.create(
                sensor=sensor,
                mac=parsed_dict.get("mac", mac),
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
                raw_data=raw,
                rssi=rssi,
                timestamp=timestamp,
                total_entries=totals_by_sensor[mac]["entries"],
                total_exits=totals_by_sensor[mac]["exits"],
            )
            created_count += 1

        return Response({"created": created_count, "errors": errors}, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)


class AirQualityDataHistoryView(APIView):
    def get(self, request):
        data = AirQualityData.objects.order_by('-timestamp')[::200]  # Get every 100th entry for performance
        return Response(AirQualityDataSerializer(data, many=True).data)

class EnergyDataHistoryView(APIView):
    def get(self, request):
        data = EnergyData.objects.order_by('-timestamp')[::200]
        return Response(EnergyDataSerializer(data, many=True).data)

class OccupancyDataHistoryView(APIView):
    def get(self, request):
        data = OccupancyData.objects.order_by('-timestamp')[::200]
        return Response(OccupancyDataSerializer(data, many=True).data)

class RadarDataHistoryView(APIView):
    def get(self, request):
        data = RadarData.objects.order_by('-timestamp')[::200] 
        serializer = RadarDataSerializer(data, many=True)
        return Response(serializer.data)

class EnergyDataHistoryViewLevel3(APIView):
    def get(self, request):
        sensor = get_object_or_404(Sensor, sensor_id='0', sensor_type='EM')
        data = EnergyData.objects.filter(sensor=sensor).order_by('-timestamp')[::200]
        return Response(EnergyDataSerializer(data, many=True).data)

class EnergyDataHistoryViewLevel4(APIView):
    def get(self, request):
        sensor = get_object_or_404(Sensor, sensor_id='1', sensor_type='EM')
        data = EnergyData.objects.filter(sensor=sensor).order_by('-timestamp')[::200]
        return Response(EnergyDataSerializer(data, many=True).data)

class Lsg01AirQualityHistoryView(APIView):
    def get(self, request):
        data = Lsg01AirQualityData.objects.order_by('-timestamp')[::500]
        return Response(Lsg01AirQualityDataSerializer(data, many=True).data)

class UnifiedAirQualityHistoryView(APIView):
    def get(self, request):
        # Fetch both AQ and LSG01 sensor data
        aq_data = AirQualityData.objects.select_related("sensor").all()
        lsg_data = Lsg01AirQualityData.objects.select_related("sensor").all()

        # Transform to a common format
        def transform_aq(entry):
            return {
                "sensor": SensorSerializer(entry.sensor).data,
                "co2": entry.co2,
                "temperature": entry.temp,
                "timestamp": entry.timestamp,
                "source": "AQ"
            }

        def transform_lsg(entry):
            return {
                "sensor": SensorSerializer(entry.sensor).data,
                "co2": entry.co2,
                "temperature": entry.temperature,
                "timestamp": entry.timestamp,
                "source": "LSG01"
            }

        unified = list(map(transform_aq, aq_data)) + list(map(transform_lsg, lsg_data))
        unified.sort(key=lambda x: x["timestamp"], reverse=True)

        return Response(unified[::200])  # Sample every 100th to reduce load




# class RadarDataCreateView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         logger.info(f"RADAR POST RECEIVED: {request.data}")
#         try:
#             data = request.data
#             radar_info = data.get("radar", {})
#             coordinates = radar_info.get("coord", {})
#             mac = data.get("mac")
            
#             # Get or create sensor
#             sensor = get_or_create_sensor(mac, 'RD', mac=mac)
            
#             record = RadarData.objects.create(
#                 sensor=sensor,
#                 mac=mac,
#                 sn=int(data.get("sn")),
#                 timestamp=data.get("timestamp"),
#                 num_targets=int(radar_info.get("num", 0)),
#                 coordinates=coordinates,
#                 raw_payload=data
#             )
#             return Response({"status": "created", "id": record.id}, status=201)
#         except Exception as e:
#             return Response({"error": str(e)}, status=400)
import traceback

class RadarDataCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # print("[DEBUG] Raw radar payload:", request.data)

            radar_info = request.data.get("radar", {})
            coordinates = radar_info.get("coord", {})
            mac = request.data.get("mac")
            sn = int(request.data.get("sn", 0))
            num_targets = int(radar_info.get("num", 0))
            timestamp = now()  # override sensor timestamp

            if not mac:
                return Response({"error": "Missing 'mac' field"}, status=400)

            # Create or fetch the sensor
            sensor = get_or_create_sensor(mac, 'RD')

            record = RadarData.objects.create(
                sensor=sensor,
                mac=mac,
                sn=sn,
                timestamp=timestamp,
                num_targets=num_targets,
                coordinates=coordinates,
                raw_payload=request.data
            )

            return Response({"status": "created", "id": record.id}, status=201)

        except Exception as e:
            print("[ERROR] RadarDataCreateView Exception:", str(e))
            # traceback.print_exc()
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
    


# class LiveRecommendationView(APIView):
#     def get(self, request):
#         # Get latest data
#         aq = AirQualityData.objects.order_by('-timestamp').first()
#         em = EnergyData.objects.order_by('-timestamp').first()
#         oc = OccupancyData.objects.order_by('-timestamp').first()

#         if not all([aq, em, oc]):
#             return Response({"error": "Insufficient sensor data."}, status=400)

#         # Prepare current state
#         current_data = {
#             "co2": aq.co2 or 0,
#             "temp": aq.temp or 0,
#             "total_act_power": em.total_act_power or 0,
#             "total_entries": oc.total_entries or 0,
#             "total_exits": oc.total_exits or 0
#         }

#         # Forecast future values
#         forecasted = {}
#         for key, model in forecast_models.items():
#             # Dummy lag-based input (you may enhance this to use real lag/rolling features)
#             input_row = pd.DataFrame([{
#                 f"{key}": current_data.get(key, 0),
#                 f"{key}_lag_1": current_data.get(key, 0) - 5,
#                 f"{key}_lag_2": current_data.get(key, 0) - 10,
#                 f"{key}_lag_3": current_data.get(key, 0) - 15,
#                 f"{key}_lag_5": current_data.get(key, 0) - 25,
#                 f"{key}_lag_10": current_data.get(key, 0) - 50,
#                 f"{key}_lag_30": current_data.get(key, 0) - 100,
#                 f"{key}_lag_60": current_data.get(key, 0) - 150,
#                 f"{key}_roll_3": current_data.get(key, 0),
#                 f"{key}_roll_5": current_data.get(key, 0),
#                 f"{key}_roll_10": current_data.get(key, 0)
#             }])
#             forecasted[f"{key}_future"] = model.predict(input_row)[0]

#         # Prepare input to recommender
#         input_row = pd.DataFrame([{
#             **current_data,
#             **forecasted
#         }])

#         encoded = recommendation_model.predict(input_row)[0]
#         action = label_encoder.inverse_transform([encoded])[0]

#         return Response({
#             "current": current_data,
#             "forecast": forecasted,
#             "recommended_action": action
#         })


# class LiveRecommendationView(APIView):
#     def get(self, request):
#         try:
#             rec_input = build_input_vector_from_latest_data()
#             if rec_input is None:
#                 return Response({"recommendation": "Insufficient sensor data"}, status=200)

#             # Predict recommended label
#             pred_label = recommendation_model.predict([rec_input])[0]
#             label = label_encoder.inverse_transform([pred_label])[0]
#             tags = label.split(";")

#             # Generate natural language summary
#             summary_main = format_recommendation(tags)

#             # Add energy usage note if available
#             energy_val = rec_input.get("total_act_power", None)
#             energy_summary = get_energy_summary(energy_val) if energy_val else ""

#             final_message = f"{summary_main} {energy_summary}".strip()

#             return Response({
#                 "recommendation": final_message,
#                 "tags": tags,
#                 "current_energy_watts": energy_val
#             })

#         except Exception as e:
#             return Response({"recommendation": "Error generating recommendation", "error": str(e)}, status=500)


class LiveRecommendationView(APIView):
    def get(self, request):
        try:
            messages = generate_recommendations_by_location()
            return Response({
                "recommendation": " ".join(messages),
                "messages": messages
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)



# Load models once at module level
# rec_model = joblib.load("models/recommendation_model.pkl")
# label_encoder = joblib.load("models/label_encoder.pkl")

# @api_view(["GET"])
# def get_recommendation(request):
#     try:
#         # Get the latest readings
#         aq = AirQualityData.objects.latest('timestamp')
#         em = EnergyData.objects.latest('timestamp')
#         oc = OccupancyData.objects.latest('timestamp')

#         # Create input for the recommendation model (adjust fields as needed)
#         row = pd.DataFrame([{
#             "co2": aq.co2,
#             "temp": aq.temp,
#             "total_act_power": em.total_act_power,
#             "total_entries": oc.total_entries,
#             "total_exits": oc.total_exits,
#             "co2_future": aq.co2 + 100,
#             "temp_future": aq.temp + 1.5,
#             "total_act_power_future": em.total_act_power + 500,
#             "total_entries_future": oc.total_entries + 10,
#             "total_exits_future": oc.total_exits + 10,
#         }])

#         prediction = recommendation_model.predict(row)[0]
#         label = label_encoder.inverse_transform([prediction])[0]

#         return Response({"recommendation": label})
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)


def format_recommendation(tags, location_summary, power_kw):
    if not tags or tags == [""]:
        return "✅ All monitored rooms are currently operating within optimal environmental conditions."

    summaries = []

    for tag in tags:
        if "HIGH_CO2" in tag:
            summaries.append(f"🌿 High CO₂ levels detected in {location_summary}. Please increase ventilation.")
        elif "HIGH_TEMP" in tag:
            summaries.append(f"🌡️ Elevated temperature in {location_summary}. Consider increasing cooling.")
        elif "HIGH_OCCUPANCY" in tag:
            summaries.append(f"👥 High occupancy in {location_summary}. Ensure good air circulation.")
        elif "HIGH_ENERGY" in tag:
            summaries.append(f"⚡ High energy usage detected in {location_summary}. Check for inefficiencies.")
        elif "LOW_TEMP" in tag:
            summaries.append(f"❄️ Low temperature detected in {location_summary}. Consider heating.")
        else:
            summaries.append(f"⚠️ {tag.replace('_', ' ').capitalize()} in {location_summary}. Please review.")

    # Add energy note
    if power_kw < 4:
        summaries.append(f"🔋 Current energy usage is {power_kw:.1f} kW (low and efficient).")
    elif 4 <= power_kw <= 7:
        summaries.append(f"⚡ Current energy usage is {power_kw:.1f} kW (normal).")
    else:
        summaries.append(f"⚠️ Current energy usage is {power_kw:.1f} kW (above optimal range).")

    return " ".join(summaries)


@api_view(["GET"])
def get_recommendation(request):
    try:
        # Get latest sensor data
        aq = AirQualityData.objects.latest("timestamp")
        em = EnergyData.objects.latest("timestamp")
        oc = OccupancyData.objects.latest("timestamp")

        location_summary = (
            getattr(aq.sensor, "floor", None) or
            getattr(em.sensor, "floor", None) or
            getattr(oc.sensor, "floor", None) or
            "an unknown location"
        )

        power_kw = em.total_act_power / 1000.0 if em.total_act_power else 0

        # Create model input
        row = pd.DataFrame([{
            "co2": aq.co2,
            "temp": aq.temp,
            "total_act_power": em.total_act_power,
            "total_entries": oc.total_entries,
            "total_exits": oc.total_exits,
            "co2_future": aq.co2 + 100,
            "temp_future": aq.temp + 1.5,
            "total_act_power_future": em.total_act_power + 500,
            "total_entries_future": oc.total_entries + 10,
            "total_exits_future": oc.total_exits + 10,
        }])

        prediction = recommendation_model.predict(row)[0]
        label = label_encoder.inverse_transform([prediction])[0]
        tags = label.split(";")

        summary = format_recommendation(tags, location_summary, power_kw)

        return Response({
            "recommendation": summary,
            "tags": tags,
            "location": location_summary,
            "current_energy_kw": round(power_kw, 2)
        })

    except Exception as e:
        traceback.print_exc()  # This will print the full error to the terminal
        return Response({"error": str(e)}, status=500)