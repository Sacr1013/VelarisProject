# Generated by Django 5.2 on 2025-04-23 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_account_locked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='account_locked',
        ),
    ]
