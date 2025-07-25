# Generated by Django 5.2 on 2025-05-13 03:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0002_booking_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booking_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('SELECTED', 'Seleccionado'), ('PENDING', 'Pendiente de pago'), ('CONFIRMED', 'Confirmado'), ('CANCELLED', 'Cancelado')], db_index=True, default='SELECTED', max_length=10),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['flight', 'status'], name='flights_boo_flight__2b72bf_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['user', 'booking_date'], name='flights_boo_user_id_906560_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['status', 'booking_date'], name='flights_boo_status_2e7e39_idx'),
        ),
    ]
