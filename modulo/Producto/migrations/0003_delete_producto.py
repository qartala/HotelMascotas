# Generated by Django 5.1 on 2024-08-27 19:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Compra', '0003_alter_carrito_idproducto_and_more'),
        ('Producto', '0002_remove_producto_id_promocion_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Producto',
        ),
    ]
