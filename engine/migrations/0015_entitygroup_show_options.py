# Generated by Django 2.0.2 on 2018-02-28 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0014_auto_20180226_0516'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitygroup',
            name='show_options',
            field=models.BooleanField(default=False),
        ),
    ]
