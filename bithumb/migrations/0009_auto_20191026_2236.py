# Generated by Django 2.2.6 on 2019-10-26 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bithumb', '0008_auto_20191026_2222'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wallet',
            old_name='money',
            new_name='monney',
        ),
    ]
