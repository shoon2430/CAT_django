# Generated by Django 2.2.6 on 2019-10-26 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bithumb', '0009_auto_20191026_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='tickerQuantity',
            field=models.FloatField(default=0),
        ),
    ]
