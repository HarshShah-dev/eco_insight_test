from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AirQualityData, EnergyData, OccupancyData, RadarData, SensorData

@receiver(post_save, sender=AirQualityData)
def create_unified_air_quality_data(sender, instance, created, **kwargs):
    if created:
        SensorData.objects.create(
            sensor=instance.sensor,
            timestamp=instance.timestamp,
            device_id=instance.device,
            quality=instance.quality,
            co2=instance.co2,
            temp=instance.temp,
            humidity=instance.humidity,
            voc=instance.voc,
            pm2p5=instance.pm2p5,
            pm10=instance.pm10,
            pm1=instance.pm1,
            pm4=instance.pm4,
            version=instance.version
        )

@receiver(post_save, sender=EnergyData)
def create_unified_energy_data(sender, instance, created, **kwargs):
    if created:
        SensorData.objects.create(
            sensor=instance.sensor,
            timestamp=instance.timestamp,
            device_id=str(instance.device_id),
            a_current=instance.a_current,
            a_voltage=instance.a_voltage,
            a_act_power=instance.a_act_power,
            a_aprt_power=instance.a_aprt_power,
            a_pf=instance.a_pf,
            a_freq=instance.a_freq,
            b_current=instance.b_current,
            b_voltage=instance.b_voltage,
            b_act_power=instance.b_act_power,
            b_aprt_power=instance.b_aprt_power,
            b_pf=instance.b_pf,
            b_freq=instance.b_freq,
            c_current=instance.c_current,
            c_voltage=instance.c_voltage,
            c_act_power=instance.c_act_power,
            c_aprt_power=instance.c_aprt_power,
            c_pf=instance.c_pf,
            c_freq=instance.c_freq,
            total_current=instance.total_current,
            total_act_power=instance.total_act_power,
            total_aprt_power=instance.total_aprt_power
        )

@receiver(post_save, sender=OccupancyData)
def create_unified_occupancy_data(sender, instance, created, **kwargs):
    if created:
        SensorData.objects.create(
            sensor=instance.sensor,
            timestamp=instance.timestamp,
            mac=instance.mac,
            frame_version=instance.frame_version,
            serial_number=instance.serial_number,
            entries=instance.entries,
            exits=instance.exits,
            total_entries=instance.total_entries,
            total_exits=instance.total_exits
        )

@receiver(post_save, sender=RadarData)
def create_unified_radar_data(sender, instance, created, **kwargs):
    if created:
        SensorData.objects.create(
            sensor=instance.sensor,
            timestamp=instance.timestamp,
            mac=instance.mac,
            radar_sn=instance.sn,
            num_targets=instance.num_targets,
            coordinates=instance.coordinates,
            raw_payload=instance.raw_payload
        ) 