from django.core.management.base import BaseCommand
from flights.models import Airport, Airline

class Command(BaseCommand):
    help = 'Genera aeropuertos y aerolíneas base'

    def handle(self, *args, **kwargs):
        # Aeropuertos
        airports_data = [
            {"code": "BOG", "name": "El Dorado", "city": "Bogotá", "country": "Colombia"},
            {"code": "MDE", "name": "José María Córdova", "city": "Medellín", "country": "Colombia"},
            {"code": "CTG", "name": "Rafael Núñez", "city": "Cartagena", "country": "Colombia"},
            {"code": "MIA", "name": "Miami Intl", "city": "Miami", "country": "USA"},
            {"code": "MAD", "name": "Barajas", "city": "Madrid", "country": "España"},
        ]

        for data in airports_data:
            Airport.objects.get_or_create(**data)

        self.stdout.write(self.style.SUCCESS(f'{len(airports_data)} aeropuertos creados o verificados.'))

        # Aerolínea
        airline_name = "Velair"
        airline, created = Airline.objects.get_or_create(name=airline_name)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Aerolínea "{airline_name}" creada.'))
        else:
            self.stdout.write(self.style.WARNING(f'Aerolínea "{airline_name}" ya existía.'))

        self.stdout.write(self.style.SUCCESS('Base de datos base poblada exitosamente.'))
