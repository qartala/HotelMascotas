# Generated by Django 5.0.4 on 2024-10-23 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuario', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='trabajador',
            field=models.BooleanField(default=False),
        ),
    ]
