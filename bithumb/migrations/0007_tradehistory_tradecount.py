# Generated by Django 2.2.6 on 2019-10-26 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bithumb', '0006_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradehistory',
            name='tradeCount',
            field=models.IntegerField(default=0),
        ),
    ]