# Generated by Django 4.0.3 on 2022-04-05 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='member',
            table='member',
        ),
        migrations.AlterModelTable(
            name='memberprofile',
            table='member_profile',
        ),
    ]
