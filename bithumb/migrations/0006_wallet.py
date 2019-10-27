# Generated by Django 2.2.6 on 2019-10-26 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bithumb', '0005_auto_20191025_0211'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.IntegerField(default=0)),
                ('tickerName', models.CharField(max_length=50, null=True)),
                ('tickerQuantity', models.IntegerField(default=0)),
                ('userId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bithumb.ProgramUser')),
            ],
        ),
    ]