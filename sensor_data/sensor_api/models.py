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
