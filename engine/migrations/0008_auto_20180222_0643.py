# Generated by Django 2.0.2 on 2018-02-22 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0007_auto_20180221_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bigrams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word1', models.CharField(max_length=100)),
                ('word2', models.CharField(max_length=100)),
                ('cnt', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='re_question',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='questionsentitygroup',
            name='re_question',
            field=models.ForeignKey(blank=True, help_text='This is the question to be asked when user enters an invalid query.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='re_question_entitytype', to='engine.Sentences'),
        ),
    ]
