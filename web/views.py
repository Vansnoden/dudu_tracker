import glob
import os
import re
import shutil
import threading
import uuid
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import Constraint, Request, Workspace
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from .utils import produce_grid, produce_neighbourhood, MONTHS, TSTEPS, run_model
import base64
from django.conf import settings
from authentication.views import authenticated
import shutil

# Create your views here.

@authenticated
def home(request):
    # userdata = UserData()
    # constraint = Constraint()
    return render(request, "web/index.html", {
        "months": MONTHS,
        "tsteps": TSTEPS
    })


def help(request):
   return render(request, "web/help.html", {}) 


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


def get_unique_id():
    return uuid.uuid4().hex


@csrf_exempt
def get_outputs(request, index=0):
    # get latest request id
    workspace = Workspace.objects.filter(user=request.user)
    workspace = workspace[0] if workspace else None
    if workspace:
        latest_request = Request.objects.filter(workspace=workspace).order_by("-create_date")
        request_data = latest_request[0] if latest_request else None
        if request_data:
            data_dir = os.path.join(settings.MEDIA_ROOT, f"workspaces/{request_data.workspace.id}/data/{request_data.req_uid}/outputs/png")
            # file_names = os.listdir(data_dir)
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
                    "next": index + 1 if index < count - 1 else 0,
                    "file": file_content,
                    "req_id": request_data.id
                })
            except Exception as e:
                return JsonResponse({
                    "num_outputs": 1,
                    "next": 0,
                    "file": "",
                    "req_id": request_data.id
                })
        else:
            return JsonResponse({
                "num_outputs": 1,
                "next": 0,
                "file": "",
                "req_id": request_data.id
            })
    else:
        return JsonResponse({
            "num_outputs": 1,
            "next": 0,
            "file": "",
            "req_id": request_data.id
        })
    

@csrf_exempt
def download_data(request):
    format = request.POST["format"]
    workspace = Workspace.objects.filter(user=request.user)
    workspace = workspace[0] if workspace else None
    if workspace:
        latest_request = Request.objects.filter(workspace=workspace).order_by("-create_date")
        request_data = latest_request[0] if latest_request else None
        if request_data:
            data_dir = os.path.join(settings.MEDIA_ROOT, f"workspaces/{request_data.workspace.id}/data/{request_data.req_uid}/outputs/{format}")
            print("### ZIPPING FILE ###")
            shutil.make_archive(os.path.join(settings.MEDIA_ROOT, f"workspaces/{request_data.workspace.id}/data/{request_data.req_uid}/outputs/{format}_output"), 'zip', data_dir)
            # output_zip_path = os.path.join(settings.MEDIA_ROOT, f"workspaces/{request_data.workspace.id}/data/{request_data.req_uid}/outputs/{format}_output")
            url_file = f"{settings.MEDIA_URL}/workspaces/{request_data.workspace.id}/data/{request_data.req_uid}/outputs/{format}_output.zip"
            return JsonResponse({
                "file": url_file
            })
    else:
        return JsonResponse({
                "file": ""
            })
    


@csrf_exempt
def process_data_form(request):
    # print(request.POST)
    workspace = request.user.get_user_workspace()
    udata = Request(
        workspace = workspace,
        shp_file = request.FILES["shp_file"],
        dbf_file = request.FILES["dbf_file"],
        shx_file = request.FILES["shx_file"],
        affected_area = request.FILES["affected_area"],
        travel_speed = float(request.POST['travel_speed']),
        cell_size = float(request.POST['cell_size']),
        req_uid = get_unique_id()
    )
    udata.save()
    num_cons = request.POST['num_cons']
    constraints = []
    for i in range(int(num_cons)):
        cx = Constraint(
            file = request.FILES['c'+str(i)],
            minimum = request.POST['c'+str(i)+'min'],
            maximum = request.POST['c'+str(i)+'max'],
            request = udata
        )
        cx.save()
        constraints.append(cx)

    duration = int(request.POST["duration"]) if "duration" in request.POST.keys() else 5
    start_year = int(request.POST["year"]) if "year" in request.POST.keys() else 2020
    start_month = request.POST["month"] if "month" in request.POST.keys() else "Jan"
    time_step = request.POST["tstep"] if "tstep" in request.POST.keys() else "Yearly"
    
    thread1 = produce_grid(workspace, udata, cellsize=udata.cell_size)
    thread1.join()
    thread2 = produce_neighbourhood(workspace, udata, spedStrg=udata.cell_size)
    thread2.join()
    thread3 = run_model(constraints, duration=duration, start_month=start_month, 
                       start_year=start_year, time_step=time_step, workspace=workspace, udata=udata)
    thread3.join()
    
    return JsonResponse({
        "success": "ok",
    })
