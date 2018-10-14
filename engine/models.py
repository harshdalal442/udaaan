from django.db import models
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from django.utils.safestring import mark_safe

# Create your models here.

# This is our Database Schema:

"""
    Seat Model:
        This denotes a seat.
        It can be assigned to only one row.
"""
class Seat(models.Model):
    seat_id = models.CharField(max_length=1000,
                               null=False,
                               blank=False)

    reserved = models.BooleanField(default=False)

    aisle = models.BooleanField(default=False)


"""
    Row Model:
        One Row can have many Seats.
"""
class Rows(models.Model):
    row_id = models.CharField(max_length=1000,
                               null=False,
                               blank=False)
    
    seats = models.ManyToManyField(Seat)    

"""
    Theatre Model:
        One Theatre can have many Rows.
"""
class Theatre(models.Model):
    theatre_name = models.CharField(max_length=1000,
                                    null=False,
                                    blank=False)

    rows = models.ManyToManyField(Rows)    

