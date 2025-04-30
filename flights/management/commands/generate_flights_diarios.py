from django.core.management.base import BaseCommand
from flights.models import Airport, Airline, Flight
from django.utils import timezone
from datetime import timedelta, datetime
import random

class Command(BaseCommand):
    help = "Genera 3 vuelos diarios por cada combinación de aeropuertos para los próximos 30 días"

    def handle(self, *args, **kwargs):
        airports = list(Airport.objects.all())
        if not airports:
            self.stdout.write(self.style.ERROR("No hay aeropuertos en la base de datos."))
            return

        airline, _ = Airline.objects.get_or_create(name="Velair")

        now = timezone.now()
        created = 0

        for origin in airports:
            for destination in airports:
                if origin != destination:
                    for day_offset in range(30):  # Próximos 30 días
                        base_date = now + timedelta(days=day_offset)
                        for i in range(3):  # 3 vuelos por día
                            departure_time = timezone.make_aware(datetime(
                                year=base_date.year,
                                month=base_date.month,
                                day=base_date.day,
                                hour=random.randint(6, 20),
                                minute=random.choice([0, 15, 30, 45])
                            ))
                            arrival_time = departure_time + timedelta(hours=random.randint(1, 6))

                            Flight.objects.create(
                                flight_number=f"VL{random.randint(1000, 9999)}",
                                airline=airline,
                                departure_airport=origin,
                                arrival_airport=destination,
                                departure_time=departure_time,
                                arrival_time=arrival_time,
                                price=random.randint(150000, 800000),
                                available_seats=random.randint(20, 100),
                                is_active=True
                            )
                            created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} vuelos creados con éxito para los próximos 30 días."))
