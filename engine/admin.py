from django.contrib import admin
from django.contrib.auth.models import Group, User
from import_export import resources
#from django.engine.models import *
from import_export.admin import ImportExportModelAdmin
from .models import *

admin.site.register(Theatre)
admin.site.register(Rows)
admin.site.register(Seat)