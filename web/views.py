import os
import threading
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Constraint, UserData
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from .utils import produce_grid, produce_neighbourhood

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


def process_data_form(request):
    data = {
        "project_folder": "",
        "shp_file": "",
        "dbf_file": "",
        "shx_file": "",
        "dbf_file": "",
        "constraints": [],
        "affected_area": "",
    }
    fn = request.FILES["pfolder"].file.name
    udata = UserData(
        project_folder = "project",
        shp_file = request.FILES["shp_file"],
        dbf_file = request.FILES["dbf_file"],
        shx_file = request.FILES["shx_file"],
        travel_speed = request.POST['travel_speed'],
        cell_size = request.POST['cell_size'],
    )
    udata.save()

    num_cons = request.POST['num_cons']
    for i in range(int(num_cons)):
        cx = Constraint(
            file = request.FILES['c'+str(i)],
            minimum = request.POST['c'+str(i)+'min'],
            maximum = request.POST['c'+str(i)+'max'],
            user_data_id = udata
        )
        cx.save()
    
    produce_grid()
    produce_neighbourhood()
    
    return JsonResponse({
        "success": "ok",
    })
