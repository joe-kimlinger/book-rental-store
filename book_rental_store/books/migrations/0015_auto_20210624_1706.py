# Generated by Django 3.2.4 on 2021-06-24 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0014_auto_20210623_2356'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_type',
            field=models.CharField(default='Novel', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(max_length=75),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=75),
        ),
    ]
