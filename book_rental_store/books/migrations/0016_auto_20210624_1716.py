# Generated by Django 3.2.4 on 2021-06-24 22:16

from django.db import migrations, models
import django.db.models.deletion


def default_book_types(apps, schema_editor):
    BookType = apps.get_model('books', 'BookType')

    # Create default book types
    BookType.objects.create(book_type='Novel', rental_rate=1.50)
    BookType.objects.create(book_type='Regular', rental_rate=1.50)
    BookType.objects.create(book_type='Fiction', rental_rate=3.00)


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_auto_20210624_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_type', models.CharField(max_length=50)),
                ('rental_rate', models.DecimalField(decimal_places=2, default=1.0, max_digits=12)),
            ],
        ),
        migrations.RunPython(default_book_types),
        migrations.RemoveField(
            model_name='book',
            name='rental_rate',
        ),
        migrations.RemoveField(
            model_name='book',
            name='book_type'
        ),
        migrations.AddField(
            model_name='book',
            name='book_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='books.booktype'),
        ),
    ]