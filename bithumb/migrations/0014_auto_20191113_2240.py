# Generated by Django 2.2.6 on 2019-11-13 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bithumb', '0013_auto_20191113_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='apilicense',
            name='nv_privateKey',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='apilicense',
            name='nv_publicKey',
            field=models.CharField(default=123, max_length=500),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='apilicense',
            name='bit_privateKey',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='apilicense',
            name='bit_publicKey',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='apilicense',
            name='tw_number',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='apilicense',
            name='tw_privateKey',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='apilicense',
            name='tw_publicKey',
            field=models.CharField(max_length=500),
        ),
    ]