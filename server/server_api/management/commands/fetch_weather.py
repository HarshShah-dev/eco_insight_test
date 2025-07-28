import logging
from django.core.management.base import BaseCommand
from server_api.weather_service import refresh_weather_for_default_location

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Fetch and upsert Open-Meteo weather for the default location."

    def handle(self, *args, **options):
        loc = refresh_weather_for_default_location()
        self.stdout.write(self.style.SUCCESS(f"Weather refreshed for {loc}"))
