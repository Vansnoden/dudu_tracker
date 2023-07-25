import threading
from django.http import JsonResponse
from django.shortcuts import render
from .models import Constraint, UserData

# Create your views here.

MONTHS = [
    "Jan","Feb","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"
]

TSTEPS = [
    "Monthly", "Yearly"
]


def home(request):
    # userdata = UserData()
    # constraint = Constraint()
    return render(request, "web/index.html", {
        "months": MONTHS,
        "tsteps": TSTEPS
    })



def get_inputs():
    return JsonResponse({})

def produce_grid():
    return None

def produce_neighbourhood():
    pass

def add_constraint():
    pass

def process_data():
    return JsonResponse({})
