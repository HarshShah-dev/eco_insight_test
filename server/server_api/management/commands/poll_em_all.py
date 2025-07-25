import datetime
import time
import requests
from django.core.management.base import BaseCommand
from server_api.models import EnergyData, Sensor

def get_or_create_sensor(sensor_id, sensor_type):
    try:
        sensor = Sensor.objects.get(sensor_id=sensor_id)
        return sensor
    except Sensor.DoesNotExist:
        sensor = Sensor.objects.create(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            description=f"Auto-created {sensor_type} sensor"
        )
        return sensor

class Command(BaseCommand):
    help = "Poll sensor data every 10 seconds and store it in the database."

    def handle(self, *args, **options):
        url = "http://192.168.68.51/rpc/EM.GetStatus?id=0"  # Using HTTPS here
        url2 = "http://192.168.68.50/rpc/EM.GetStatus?id=0"
        self.stdout.write("Starting sensor polling... (Press CTRL+C to stop)")
        
        # Optionally, disable warnings about insecure requests:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        while True:
            try:
                # Pass verify=False to bypass SSL certificate verification
                response = requests.get(url, verify=False)
                response2 = requests.get(url2, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write(f"Received data from Level 3: {data}")

                    # Get or create sensor for Level 3
                    sensor = get_or_create_sensor('0', 'EM')

                    em_record = EnergyData(
                        sensor=sensor,
                        device_id=0,
                        a_current=data.get("a_current"),
                        a_voltage=data.get("a_voltage"),
                        a_act_power=data.get("a_act_power"),
                        a_aprt_power=data.get("a_aprt_power"),
                        a_pf=data.get("a_pf"),
                        a_freq=data.get("a_freq"),
                        b_current=data.get("b_current"),
                        b_voltage=data.get("b_voltage"),
                        b_act_power=data.get("b_act_power"),
                        b_aprt_power=data.get("b_aprt_power"),
                        b_pf=data.get("b_pf"),
                        b_freq=data.get("b_freq"),
                        c_current=data.get("c_current"),
                        c_voltage=data.get("c_voltage"),
                        c_act_power=data.get("c_act_power"),
                        c_aprt_power=data.get("c_aprt_power"),
                        c_pf=data.get("c_pf"),
                        c_freq=data.get("c_freq"),
                        # n_current=data.get("n_current"),
                        total_current=data.get("total_current"),
                        total_act_power=data.get("total_act_power"),
                        total_aprt_power=data.get("total_aprt_power"),
                        # user_calibrated_phase=data.get("user_calibrated_phase"),
                        timestamp=datetime.datetime.now()  # Use the current time
                    )
                    em_record.save()
                    self.stdout.write("Level 3 Data saved successfully.")


                if response2.status_code == 200:
                    data2 = response2.json()
                    self.stdout.write(f"Received data from Level 4: {data2}")

                    # Get or create sensor for Level 4
                    sensor2 = get_or_create_sensor('1', 'EM')

                    em_record2 = EnergyData(
                        sensor=sensor2,
                        device_id=1,
                        a_current=data2.get("a_current"),
                        a_voltage=data2.get("a_voltage"),
                        a_act_power=data2.get("a_act_power"),
                        a_aprt_power=data2.get("a_aprt_power"),
                        a_pf=data2.get("a_pf"),
                        a_freq=data2.get("a_freq"),
                        b_current=data2.get("b_current"),
                        b_voltage=data2.get("b_voltage"),
                        b_act_power=data2.get("b_act_power"),
                        b_aprt_power=data2.get("b_aprt_power"),
                        b_pf=data2.get("b_pf"),
                        b_freq=data2.get("b_freq"),
                        c_current=data2.get("c_current"),
                        c_voltage=data2.get("c_voltage"),
                        c_act_power=data2.get("c_act_power"),
                        c_aprt_power=data2.get("c_aprt_power"),
                        c_pf=data2.get("c_pf"),
                        c_freq=data2.get("c_freq"),
                        # n_current=data.get("n_current"),
                        total_current=data2.get("total_current"),
                        total_act_power=data2.get("total_act_power"),
                        total_aprt_power=data2.get("total_aprt_power"),
                        # user_calibrated_phase=data.get("user_calibrated_phase"),
                        timestamp=datetime.datetime.now()  # Use the current time
                    )
                    em_record2.save()
                    self.stdout.write("Level 4 Data saved successfully.")
                else:
                    self.stdout.write(f"Failed to retrieve data. Status code: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"Error occurred: {e}")

            time.sleep(10)
