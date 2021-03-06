# Generated by Django 2.2.6 on 2019-11-13 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bithumb', '0012_auto_20191108_0004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wallet',
            name='tickerName',
        ),
        migrations.AddField(
            model_name='tradehistory',
            name='schedulerId',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='tradescheduler',
            name='endMoney',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tradescheduler',
            name='endTickerQuantity',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='tradescheduler',
            name='startMoney',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tradescheduler',
            name='startTickerQuantity',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='tradescheduler',
            name='ticker',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tradescheduler',
            name='tradeYield',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='wallet',
            name='ticker',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='programuser',
            name='mySchedulerId',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='programuser',
            name='userName',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tradehistory',
            name='ticker',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tradehistory',
            name='tradeInfo',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tradescheduler',
            name='schedulerId',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
