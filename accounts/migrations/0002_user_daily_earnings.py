# Generated by Django 3.0 on 2021-03-03 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='daily_earnings',
            field=models.FloatField(default=0.0, max_length=9),
        ),
    ]
