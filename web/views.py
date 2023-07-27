import glob
import os
import re
import threading
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Constraint, UserData
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from .utils import produce_grid, produce_neighbourhood, MONTHS, TSTEPS, run_model
import base64
from django.conf import settings

# Create your views here.


def home(request):
    # userdata = UserData()
    # constraint = Constraint()
    return render(request, "web/index.html", {
        "months": MONTHS,
        "tsteps": TSTEPS
    })


def sort_output_names(datalist):
    num_list = [(int(re.search(r'\d+', os.path.basename(x)).group()), datalist.index(x))  for x in datalist]
    sorted_data = []
    for j in list(range(len(num_list) - 1)):
        for i in list(range(len(num_list) - 1)):
            curr = num_list[i][0]
            next = num_list[i+1][0]
            if curr > next:
                val = num_list[i+1]
                num_list[i+1] = num_list[i]
                num_list[i] = val
    for v,i in num_list:
        sorted_data.append(datalist[i]);
    return sorted_data


@csrf_exempt
def get_outputs(request, index=0):
    data_dir = os.path.join(settings.BASE_DIR, "static/data/outputs/png") 
    file_names = os.listdir(data_dir)
    filelist = glob.glob(os.path.join(data_dir, 'Spread*.png'))
    filelist = sorted(filelist)
    filelist = sort_output_names(filelist)
    try:
        # file_names = file_names.sort()
        count = len(filelist)
        # index = request.POST["index"] if "index" in request.POST.keys() else 0
        f = os.path.join(data_dir, filelist[index])
        # checking if it is a file
        file = None
        file_content = ""
        if os.path.isfile(f):
            file = open(f,"rb")
            file_content = base64.b64encode(file.read()).decode('ascii')
        return JsonResponse({
            "num_outputs": count,
            "next": index + 1 if index < count else 0,
            "file": file_content
        })
    except Exception as e:
        return JsonResponse({
            "num_outputs": 1,
            "next": 0,
            "file": ""
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
    # fn = request.FILES["pfolder"].file.name
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
    constraints = []
    for i in range(int(num_cons)):

        cx = Constraint(
            file = request.FILES['c'+str(i)],
            minimum = request.POST['c'+str(i)+'min'],
            maximum = request.POST['c'+str(i)+'max'],
            user_data_id = udata
        )
        cx.save()
        constraints.append(cx)
    
    produce_grid()
    produce_neighbourhood()
    run_model(constraints, duration=24, start_month='Jan', start_year=2020, time_step="Yearly")
    
    return JsonResponse({
        "success": "ok",
    })
