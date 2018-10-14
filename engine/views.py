from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from .models import *
from .utils import *

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

"""
    This is the function which is called to initiate a theatre.
    It initally obtains data from the request.

    Then once it has verified that the data obtained is according to the format, 
    it further checks if there is aldready a theatre with the same name.

    If there is no theatre with the given name, it creates another theatre.
"""
class RegisterScreenAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data
        
        name = data.get('name', False)
        seat_info = data.get('seatInfo', False)

        if name == False or seat_info == False:
            return Response(data=return_dict("121","Wrong input format"))

        name = name.strip()

        if check_theatre_aldready_registered(name):
            return Response(data=return_dict("122","Theatre Aldready Present"))            

        add_screen_to_db(name, seat_info)

        return Response(data=return_dict("200","Screen Added Succesfully"))

"""
    This is the function which is called to register seats.

    As we have simply set up a database. It will just go to the
    particular seats of the given database and if all the seats are
    unreserved it will give the corresponding output.
"""
class RegisterSeatAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, theatre_name):
        data = request.data
                
        seat_info = data.get('seats', False)
        
        if seat_info == False:
            return Response(data=return_dict("121","Wrong input format"))

        if not check_theatre_aldready_registered(theatre_name):
            return Response(data=return_dict("122","Theatre Not Present"))            

        if check_screens_available(theatre_name, seat_info):
            reserve_seats(theatre_name, seat_info)
            return Response(data=return_dict("200","Screens Reserved"))
        else:
            return Response(data=return_dict("404","Not Possible. Seats Aldready Booked Or Invalid Input"))

"""
    This is the function which is called to Retreive seat info.

    Based on the database values and some helper functions, it 
    does what is needed.
"""
class RetreiveSeatInfoAPIView(APIView):
    def get(self, request, theatre_name):
        data = request.GET

        print(data)
        if not check_theatre_aldready_registered(theatre_name):
            return Response(data=return_dict("122","Theatre Not Present"))            

        status = data.get('status', False)
        if status == "unreserved":
            return Response(data={"availableSeats":get_unreserved_seats(theatre_name)})

        numSeats = data.get('numSeats', False)
        choice = data.get('choice', False)

        if numSeats == False or choice == False:
            return Response(data=return_dict("404","Invalid Input"))

        return Response(data={"available_seats":get_related_seats(numSeats, choice, theatre_name)})

RegisterScreen = RegisterScreenAPIView.as_view()
RegisterSeat = RegisterSeatAPIView.as_view()
RetreiveSeatInfo = RetreiveSeatInfoAPIView.as_view()