# Generated by Django 2.0.2 on 2018-02-21 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(blank=True, default='web', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(blank=True, default='eng', max_length=100, null=True),
        ),
    ]
