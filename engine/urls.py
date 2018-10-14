from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^screens/$', views.RegisterScreen),
    url(r'^screens/(?P<theatre_name>[a-zA-Z0-9]+)/reserve/$', views.RegisterSeat),
    url(r'^screens/(?P<theatre_name>[a-zA-Z0-9]+)/seats', views.RetreiveSeatInfo),    
]

