# Generated by Django 3.2.4 on 2021-06-24 22:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0016_auto_20210624_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='book_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='books.booktype'),
        ),
        migrations.AlterField(
            model_name='book',
            name='renting_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]