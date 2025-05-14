from django.core.management.base import BaseCommand
from flights.models import Flight, Seat
from django.db.models import Count

class Command(BaseCommand):
    help = 'Crea asientos para todos los vuelos que no los tengan'

    def handle(self, *args, **options):
        flights_without_seats = Flight.objects.annotate(
            seat_count=Count('seats')
        ).filter(seat_count=0)
        
        self.stdout.write(f"Encontrados {flights_without_seats.count()} vuelos sin asientos")
        
        for flight in flights_without_seats:
            self.stdout.write(f"Creando asientos para vuelo {flight.flight_number}...")
            if flight.create_seats():
                self.stdout.write(self.style.SUCCESS(f"Asientos creados para {flight.flight_number}"))
            else:
                self.stdout.write(self.style.ERROR(f"Error creando asientos para {flight.flight_number}"))