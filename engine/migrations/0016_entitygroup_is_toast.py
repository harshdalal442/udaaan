# Generated by Django 2.0.2 on 2018-02-28 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0015_entitygroup_show_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitygroup',
            name='is_toast',
            field=models.BooleanField(default=False),
        ),
    ]