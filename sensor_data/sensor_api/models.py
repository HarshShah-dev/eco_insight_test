from django.db import models

# Create your models here.

# class SensorReading(models.Model):

#     co2 = models.IntegerField()
#     humidity = models.IntegerField()
#     pm_10 = models.FloatField()
#     pm_4 = models.FloatField()
#     pm_2p5 = models.FloatField()
#     pm_1 = models.FloatField()
#     temperature = models.IntegerField()
#     tvoc_index = models.IntegerField()
#     timestamp = models.IntegerField()
#     device_id = models.CharField(max_length=100)
#     company_name = models.CharField(max_length=50)
  

#     def __str__(self):
#         return f"Sensor {self.sensor_id} at {self.timestamp}"


class SensorData(models.Model):

    device = models.CharField(max_length=100)
    quality = models.CharField(max_length=50)
    co2 = models.IntegerField()
    temp = models.IntegerField()
    humidity = models.IntegerField()
    voc = models.IntegerField()
    pm2p5 = models.FloatField()
    pm10 = models.FloatField()
    pm1 = models.FloatField()
    pm4 = models.FloatField()
    timestamp = models.IntegerField()
    version = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.device} @ {self.timestamp}"


class EMData(models.Model):
    
    device_id = models.IntegerField()
    a_current = models.FloatField()
    a_voltage = models.FloatField()
    a_act_power = models.FloatField()
    a_aprt_power = models.FloatField()
    a_pf = models.FloatField()
    a_freq = models.FloatField()
    b_current = models.FloatField()
    b_voltage = models.FloatField()
    b_act_power = models.FloatField()
    b_aprt_power = models.FloatField()
    b_pf = models.FloatField()
    b_freq = models.FloatField()
    c_current = models.FloatField()
    c_voltage = models.FloatField()
    c_act_power = models.FloatField()
    c_aprt_power = models.FloatField()
    c_pf = models.FloatField()
    c_freq = models.FloatField()
    # n_current = models.FloatField()
    total_current = models.FloatField()
    total_act_power = models.FloatField()
    total_aprt_power = models.FloatField()
    # user_calibrated_phase = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.device_id} @ {self.timestamp}"


class RawSensorData(models.Model):
    raw_data = models.JSONField()  # Stores the entire JSON payload
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data received at {self.received_at}"