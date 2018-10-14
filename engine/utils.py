from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from .models import *

"""
	Generated a dictionary based on code and message
"""
def return_dict(code, message):
    temp_dict = {"code":code, "Message":message}
    return temp_dict

"""
	Checks if aldready theatre present in db.
"""
def check_theatre_aldready_registered(name):
    return Theatre.objects.filter(theatre_name=name).exists()

"""
	Checks if value is present in array.
"""
def exists_in_array(value, array):
    for val in array:
        if val == value:
            return True
    return False

"""
	Adds a row to the db.
"""
def add_row_to_db(row_name, number_of_seats, aisle_seats):
    current_row = Rows.objects.create(row_id=row_name)
    for i in range(number_of_seats):
        is_aisle = exists_in_array(i, aisle_seats)
        seat = Seat.objects.create(seat_id=i, aisle=is_aisle)
        current_row.seats.add(seat)

    return current_row

"""
	Adds a screen to db.
"""
def add_screen_to_db(name, seat_info):
    theatre = Theatre.objects.create(theatre_name=name)
    for key, value in seat_info.items():
        row_name = key
        number_of_seats = value["numberOfSeats"]
        aisle_seats = value["aisleSeats"]

        current_row = add_row_to_db(row_name, number_of_seats, aisle_seats)        
        theatre.rows.add(current_row)

"""
	Gets a row from db.
"""
def get_row_from_all_rows(theatre, row_name):
    all_rows = theatre.rows.all()
    for row in all_rows:
        if row.row_id == row_name:            
            return row
    return False #handle later

"""
	Gets a seat from db.
"""
def get_seat_from_row(row, seat_name):    
    all_seats = row.seats.all()
    for seat in all_seats:        
        if str(seat.seat_id) == str(seat_name):
            return seat
    return False

"""
	Given seat_info, checks if all the seats are available.
"""
def check_screens_available(theatre_name, seat_info):
    theatre = Theatre.objects.get(theatre_name=theatre_name)

    is_available = True
    for key, value in seat_info.items():
        row_name = key
        seat_names = value

        row = get_row_from_all_rows(theatre, row_name)
        if row is False:
            return row

        for seat in seat_names:
            seat_obj = get_seat_from_row(row, seat)
            if seat_obj is False:
                return seat_obj
            if seat_obj.reserved:
                is_available = False

    return is_available

"""
	Reserves Seats if they are available.
"""
def reserve_seats(theatre_name, seat_info):
    theatre = Theatre.objects.get(theatre_name=theatre_name)

    for key, value in seat_info.items():
        row_name = key
        seat_names = value

        row = get_row_from_all_rows(theatre, row_name)
        if row is False:
            return row

        for seat in seat_names:
            seat_obj = get_seat_from_row(row, seat)
            if seat_obj is False:
                return seat_obj

            seat_obj.reserved = True
            seat_obj.save()

"""
	Gets all unreserved seats given a row.
"""
def get_all_unreserved_seats_from_row(row):
    unreserved_seats = []
    for seat in row.seats.all():
        if not seat.reserved:
            unreserved_seats.append(seat.seat_id)
    return unreserved_seats

"""
	Gets all unreserved seats given a theatre.
"""
def get_unreserved_seats(theatre_name):
    theatre = Theatre.objects.get(theatre_name=theatre_name)
    rows = theatre.rows.all()

    unreserved_dict = {}
    for row in rows:
        seats = get_all_unreserved_seats_from_row(row)
        unreserved_dict[row.row_id] = seats

    return unreserved_dict

"""
	Extracts row and seats from given string.
	E.g. A4, row_id=A, seat_id=4.
"""
def extract_row_id(choice):
    row_id = ""
    seat_id = ""
    flag = False
    for char in choice:
        if char.isdigit():
            flag = True
        if flag:
            seat_id = seat_id + char
        else:
            row_id = row_id + char

    return row_id, seat_id

from collections import OrderedDict

"""
	Custom Algorithm to give seats based on choice and number of seats.
"""
def get_related_seats(number_of_seats, choice, theatre_name):
    row_id, seat_id = extract_row_id(choice)
    range_start = int(seat_id) - int(number_of_seats)
    if range_start < 0:
        range_start = 0
    range_end = int(seat_id) + int(number_of_seats)

    theatre = Theatre.objects.get(theatre_name=theatre_name)
    row = get_row_from_all_rows(theatre, row_id)
    if row is False:
        return return_dict("404","My backend engine is noob. Needs an upgrade")

    aisle_started = 0
    aisle_flag = False
    available_seats = OrderedDict()

    seats = row.seats.all()
    for seat in seats:
        if seat.aisle:
            if aisle_flag is False:
                aisle_started = aisle_started + 1
                aisle_flag = True
            elif aisle_flag is True:
                aisle_flag = False
        if int(seat.seat_id) >= range_start and int(seat.seat_id) <= range_end and not seat.reserved:
            available_seats[seat.seat_id] = aisle_started

    print(available_seats)

    answer_seats = []
    for key, value in available_seats.items():
        current_seat = key
        current_column = value

        temp_seat = int(key)
        flag = True        
        for i in range(int(number_of_seats)-1):
            temp_seat = temp_seat + 1
            if str(temp_seat) in available_seats:
                if available_seats[str(temp_seat)] == current_column:
                    pass
                else:
                    flag = False
            else:
                flag = False

        if flag:
            answer_seats.append(int(key))
            temp_seat = int(key)
            for i in range(int(number_of_seats)-1):
                temp_seat = temp_seat + 1
                if str(temp_seat) in available_seats:
                    if available_seats[str(temp_seat)] == current_column:
                        answer_seats.append(temp_seat)
            break            

    return {row_id:answer_seats}
