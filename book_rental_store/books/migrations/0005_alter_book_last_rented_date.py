# Generated by Django 3.2.4 on 2021-06-22 22:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_alter_book_rented'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='last_rented_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
