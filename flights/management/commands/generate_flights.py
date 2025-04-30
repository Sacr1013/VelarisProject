from django.core.management.base import BaseCommand
from flights.models import Airport, Airline, Flight
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Genera vuelos de muestra entre aeropuertos existentes'

    def handle(self, *args, **kwargs):
        airports = list(Airport.objects.all())
        airline = Airline.objects.first()

        if not airline:
            self.stdout.write(self.style.ERROR('No hay aerolíneas creadas.'))
            return

        count = 0
        for origin in airports:
            for destination in airports:
                if origin != destination:
                    existing = Flight.objects.filter(
                        departure_airport=origin,
                        arrival_airport=destination,
                        departure_time__gte=timezone.now()
                    )
                    if existing.count() < 3:
                        for _ in range(3 - existing.count()):
                            departure_time = timezone.now() + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
                            arrival_time = departure_time + timedelta(hours=random.randint(1, 6))
                            Flight.objects.create(
                                flight_number=f"VL{random.randint(100, 999)}",
                                airline=airline,
                                departure_airport=origin,
                                arrival_airport=destination,
                                departure_time=departure_time,
                                arrival_time=arrival_time,
                                price=random.randint(150000, 800000),
                                available_seats=random.randint(10, 100),
                                is_active=True
                            )
                            count += 1

        self.stdout.write(self.style.SUCCESS(f'{count} vuelos creados.'))
