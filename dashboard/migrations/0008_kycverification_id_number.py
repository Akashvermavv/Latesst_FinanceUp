# Generated by Django 3.0 on 2021-03-26 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_kycverification_other_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='kycverification',
            name='id_number',
            field=models.CharField(default=None, max_length=50, unique=True),
            preserve_default=False,
        ),
    ]
