# Generated by Django 2.2.6 on 2019-10-26 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bithumb', '0007_tradehistory_tradecount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tradehistory',
            old_name='TradeUserId',
            new_name='userId',
        ),
    ]