# Generated by Django 5.2 on 2025-05-06 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('SELECTED', 'Seleccionado'), ('PENDING', 'Pendiente de pago'), ('CONFIRMED', 'Confirmado'), ('CANCELLED', 'Cancelado')], default='SELECTED', max_length=10),
        ),
    ]
