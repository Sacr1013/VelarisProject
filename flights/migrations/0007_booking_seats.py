# Generated by Django 5.2 on 2025-05-27 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0006_airport_lat_airport_lng'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='seats',
            field=models.ManyToManyField(related_name='bookings', to='flights.seat', verbose_name='Asientos seleccionados'),
        ),
    ]
