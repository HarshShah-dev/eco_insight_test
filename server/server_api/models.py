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


class AirQualityData(models.Model):
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, related_name='aq_data', null=True, blank=True)
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
    timestamp = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=50)
    action = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.device} @ {self.timestamp}"

    def determine_action(self):
        actions = []
        if self.co2 > 1000:
            actions.append('ALERT - HIGH_CO2 - Increase Ventilation')
        elif self.co2 > 800:
            actions.append('HIGH_CO2 - Increase Ventilation')
        if self.pm2p5 > 35:
            actions.append('HIGH_PM2P5 - Increase Ventilation')
        if self.temp > 30:
            actions.append('ALERT - HIGH_TEMP - Increase Cooling')
        elif self.temp > 26:
            actions.append('HIGH_TEMP - Increase Cooling')
        if self.temp < 18:
            actions.append('LOW_TEMP - Increase Heating')
        return ' | '.join(actions) if actions else 'NORMAL_AQ'

    def save(self, *args, **kwargs):
        if not self.action:
            self.action = self.determine_action()
        super().save(*args, **kwargs)


class EnergyData(models.Model):
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, related_name='em_data', null=True, blank=True)
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
    action = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.device_id} @ {self.timestamp}"

    def determine_action(self):
        if self.total_act_power > 7000:
            return 'HIGH_POWER_USAGE'
        if self.a_current > 10:
            return 'HIGH_CURRENT'
        return 'NORMAL_EM'

    def save(self, *args, **kwargs):
        if not self.action:
            self.action = self.determine_action()
        super().save(*args, **kwargs)


class RawSensorData(models.Model):
    raw_data = models.JSONField()  # Stores the entire JSON payload
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data received at {self.received_at}"
    
class OccupancyData(models.Model):
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, related_name='oc_data', null=True, blank=True)
    mac = models.CharField(max_length=50, blank=True, null=True)
    frame_version = models.CharField(max_length=10, blank=True, null=True)
    battery = models.IntegerField(blank=True, null=True)
    firmware_version = models.CharField(max_length=20, blank=True, null=True)
    peripheral_support = models.CharField(max_length=50, blank=True, null=True)
    salt = models.CharField(max_length=10, blank=True, null=True)
    digital_signature = models.CharField(max_length=10, blank=True, null=True)
    usage = models.CharField(max_length=10, blank=True, null=True)
    serial_number = models.IntegerField(blank=True, null=True)
    entries = models.IntegerField(blank=True, null=True)
    exits = models.IntegerField(blank=True, null=True)
    random_number = models.CharField(max_length=10, blank=True, null=True)
    raw_data = models.TextField()
    rssi = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_entries = models.IntegerField(default=0)
    total_exits = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return f"{self.mac} @ {self.timestamp}"
    
    def determine_action(self):
        if self.total_entries > (self.total_exits + 100):
            return 'VERY_POPULATED - Increase HVAC'
        if self.total_entries <= self.total_exits:
            return 'Decrease HVAC'
        if self.entries and self.entries > 0:
            return 'ENTRY_DETECTED'
        if self.exits and self.exits > 0:
            return 'EXIT_DETECTED'
        return 'NO_MOVEMENT'

    def save(self, *args, **kwargs):
        if not self.action:
            self.action = self.determine_action()
        super().save(*args, **kwargs)
    

class Sensor(models.Model):
    SENSOR_TYPES = [
        ('EM', 'Energy Meter'),
        ('AQ', 'Air Quality'),
        ('OC', 'Occupancy'),
        ('RD', 'Radar'),
    ]
    sensor_id = models.CharField(max_length=100, unique=True)
    sensor_type = models.CharField(max_length=2, choices=SENSOR_TYPES)
    floor = models.IntegerField(blank=True, null=True)
    office = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_sensor_type_display()} {self.sensor_id} @ {self.floor}/{self.office}"
    

class RadarData(models.Model):
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, related_name='radar_data', null=True, blank=True)
    mac = models.CharField(max_length=100)
    sn = models.IntegerField()  # Sequence number
    timestamp = models.DateTimeField(auto_now_add=True)
    num_targets = models.IntegerField()
    coordinates = models.JSONField()  # Store raw 'coord' field
    raw_payload = models.JSONField()  # Save original JSON (optional)
    action = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"RadarData from {self.mac} at {self.timestamp}"

    def determine_action(self):
        if self.num_targets > 3:
            return 'VERY_POPULATED - Increase HVAC'
        return 'NO_MOVEMENT'

    def save(self, *args, **kwargs):
        if not self.action:
            self.action = self.determine_action()
        super().save(*args, **kwargs)
    

class SensorData(models.Model):
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, related_name='all_data')
    timestamp = models.DateTimeField()
    action = models.CharField(max_length=255, blank=True, null=True)
    
    # Common fields that might be present in any sensor data
    device_id = models.CharField(max_length=100, blank=True, null=True)
    mac = models.CharField(max_length=50, blank=True, null=True)
    
    # Air Quality specific fields
    quality = models.CharField(max_length=100, blank=True, null=True)
    co2 = models.IntegerField(blank=True, null=True)
    temp = models.IntegerField(blank=True, null=True)
    humidity = models.IntegerField(blank=True, null=True)
    voc = models.IntegerField(blank=True, null=True)
    pm2p5 = models.FloatField(blank=True, null=True)
    pm10 = models.FloatField(blank=True, null=True)
    pm1 = models.FloatField(blank=True, null=True)
    pm4 = models.FloatField(blank=True, null=True)
    version = models.CharField(max_length=100, blank=True, null=True)
    
    # Energy Meter specific fields
    a_current = models.FloatField(blank=True, null=True)
    a_voltage = models.FloatField(blank=True, null=True)
    a_act_power = models.FloatField(blank=True, null=True)
    a_aprt_power = models.FloatField(blank=True, null=True)
    a_pf = models.FloatField(blank=True, null=True)
    a_freq = models.FloatField(blank=True, null=True)
    b_current = models.FloatField(blank=True, null=True)
    b_voltage = models.FloatField(blank=True, null=True)
    b_act_power = models.FloatField(blank=True, null=True)
    b_aprt_power = models.FloatField(blank=True, null=True)
    b_pf = models.FloatField(blank=True, null=True)
    b_freq = models.FloatField(blank=True, null=True)
    c_current = models.FloatField(blank=True, null=True)
    c_voltage = models.FloatField(blank=True, null=True)
    c_act_power = models.FloatField(blank=True, null=True)
    c_aprt_power = models.FloatField(blank=True, null=True)
    c_pf = models.FloatField(blank=True, null=True)
    c_freq = models.FloatField(blank=True, null=True)
    total_current = models.FloatField(blank=True, null=True)
    total_act_power = models.FloatField(blank=True, null=True)
    total_aprt_power = models.FloatField(blank=True, null=True)
    
    # Occupancy specific fields
    frame_version = models.CharField(max_length=10, blank=True, null=True)
    serial_number = models.IntegerField(blank=True, null=True)
    entries = models.IntegerField(blank=True, null=True)
    exits = models.IntegerField(blank=True, null=True)
    total_entries = models.IntegerField(default=0)
    total_exits = models.IntegerField(default=0)
    
    # Radar specific fields
    sn = models.IntegerField(blank=True, null=True)
    num_targets = models.IntegerField(blank=True, null=True)
    coordinates = models.JSONField(blank=True, null=True)
    raw_payload = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.sensor} @ {self.timestamp} - {self.action}"

    def determine_action(self):
        """Determine the action based on sensor type and data values"""
        if self.sensor.sensor_type == 'AQ':
            # Air Quality action rules
            actions = []
            if self.co2 and self.co2 > 1000:
                actions.append('ALERT - HIGH_CO2 - Increase Ventilation')
            if self.co2 and self.co2 > 800:
                actions.append('HIGH_CO2 - Increase Ventilation')
            if self.pm2p5 and self.pm2p5 > 35:
                actions.append('HIGH_PM2P5 - Increase Ventilation')
            if self.pm10 and self.pm10 > 100:
                actions.append('HIGH_PM10 - Increase Ventilation')
            if self.voc and self.voc > 220:
                actions.append('HIGH_VOC - Increase Ventilation')
            if self.temp and self.temp > 30:
                actions.append('ALERT - HIGH_TEMP - Increase Cooling')
            elif self.temp and self.temp > 26:
                actions.append('HIGH_TEMP - Increase Cooling')
            if self.temp and self.temp < 18:
                actions.append('LOW_TEMP - Increase Heating')
            
            return ' | '.join(actions) if actions else 'NORMAL_AQ'
            
        elif self.sensor.sensor_type == 'EM':
            # Energy Meter action rules
            if self.total_act_power and self.total_act_power > 7000:
                return 'HIGH_POWER_USAGE'
            if self.a_current and self.a_current > 10:
                return 'HIGH_CURRENT'
            return 'NORMAL_EM'
            
        elif self.sensor.sensor_type == 'OC':
            # Occupancy action rules
            if self.total_entries and self.total_entries > (self.total_exits+100):
                return 'VERY_POPULATED - Increase HVAC'
            if self.total_entries and self.total_entries <= (self.total_exits):
                return 'Decrease HVAC'
            if self.entries and self.entries > 0:
                return 'ENTRY_DETECTED'
            if self.exits and self.exits > 0:
                return 'EXIT_DETECTED'
            return 'NO_MOVEMENT'
            
        elif self.sensor.sensor_type == 'RD':
            # Radar action rules
            if self.num_targets and self.num_targets > 3:
                return 'VERY_POPULATED - Increase HVAC'
            return 'NO_MOVEMENT'
            
        return 'UNKNOWN'

    def save(self, *args, **kwargs):
        if not self.action:
            self.action = self.determine_action()
        super().save(*args, **kwargs)
    