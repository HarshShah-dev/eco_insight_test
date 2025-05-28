import time
import datetime

import requests
from django.core.management.base import BaseCommand
from server_api.models import AirQualityData, Sensor

class Command(BaseCommand):
    help = "Poll sensor data every 10 seconds and store it in the database."

    def handle(self, *args, **options):
        url = "https://sb5-244cabf81d20.local/data"  # Using HTTPS here
        self.stdout.write("Starting sensor polling... (Press CTRL+C to stop)")
        
        # Optionally, disable warnings about insecure requests:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        while True:
            try:
                # Pass verify=False to bypass SSL certificate verification
                response = requests.get(url, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write(f"Received data: {data}")
                    
                    sensor_record = AirQualityData(
                        device=data.get("device"),
                        quality=data.get("quality"),
                        co2=data.get("co2"),
                        temp=data.get("temp"),
                        humidity=data.get("humidity"),
                        voc=data.get("voc"),
                        pm2p5=data.get("pm2p5"),
                        pm10=data.get("pm10"),
                        pm1=data.get("pm1"),
                        pm4=data.get("pm4"),
                        timestamp=datetime.datetime.now(),
                        version=data.get("version")
                    )
                    sensor_record.save()
                    self.stdout.write("Data saved successfully.")
                else:
                    self.stdout.write(f"Failed to retrieve data. Status code: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"Error occurred: {e}")

            time.sleep(10)


# class Command(BaseCommand):
#     help = "Poll sensor data every 10 seconds and store it in the database."

#     def handle(self, *args, **options):
#         url = "https://sb5-244cabf81d20.local/data"
#         self.stdout.write("Starting sensor polling... (Press CTRL+C to stop)")
#         while True:
#             try:
#                 response = requests.get(url)
#                 if response.status_code == 200:
#                     data = response.json()
#                     self.stdout.write(f"Received data: {data}")
                    
#                     # Create and save a new SensorData record
#                     sensor_record = SensorData(
#                         device=data.get("device", ""),
#                         quality=data.get("quality", ""),
#                         co2=data.get("co2", 0),
#                         temp=data.get("temp", 0),
#                         humidity=data.get("humidity", 0),
#                         voc=data.get("voc", 0),
#                         pm2p5=data.get("pm2p5", 0.0),
#                         pm10=data.get("pm10", 0.0),
#                         pm1=data.get("pm1", 0.0),
#                         pm4=data.get("pm4", 0.0),
#                         timestamp=data.get("timestamp", 0),
#                         version=data.get("version", "")
#                     )
#                     sensor_record.save()
#                     self.stdout.write("Data saved successfully.")
#                 else:
#                     self.stdout.write(f"Failed to retrieve data. Status code: {response.status_code}")
#             except Exception as e:
#                 self.stdout.write(f"Error occurred: {e}")

#             # Wait 10 seconds before polling again
#             time.sleep(10)
