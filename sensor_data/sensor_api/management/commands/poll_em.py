import datetime
import time
import requests
from django.core.management.base import BaseCommand
from sensor_api.models import EMData

class Command(BaseCommand):
    help = "Poll sensor data every 10 seconds and store it in the database."

    def handle(self, *args, **options):
        url = "http://192.168.68.51/rpc/EM.GetStatus?id=0"  # Using HTTPS here
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
                    
                    em_record = EMData(
                        device_id=data.get("id"),
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
                    self.stdout.write("Data saved successfully.")
                else:
                    self.stdout.write(f"Failed to retrieve data. Status code: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"Error occurred: {e}")

            time.sleep(10)
