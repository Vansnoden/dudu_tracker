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
import logging

logger = logging.getLogger(__name__)


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
            # filelist = glob.glob(os.path.join(data_dir, 'Spread*.png'))
            filelist = sorted(Path(data_dir).iterdir(), key=os.path.getmtime)
            # filelist = sort_output_names(filelist)
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
@authenticated
def download_data(request):
    fmt = request.POST.get("format")
    if not fmt:
        return JsonResponse({"error": "missing 'format'", "file": ""}, status=400)

    workspace = Workspace.objects.filter(user=request.user).first()
    if not workspace:
        logger.warning("download_data: no workspace for user=%s", request.user)
        return JsonResponse({"error": "no workspace", "file": ""}, status=400)

    request_data = (
        Request.objects.filter(workspace=workspace).order_by("-create_date").first()
    )
    if not request_data:
        logger.warning("download_data: no request for workspace=%s", workspace.pk)
        return JsonResponse({"error": "no request", "file": ""}, status=400)

    base_rel = (
        f"workspaces/{request_data.workspace.id}/data/"
        f"{request_data.req_uid}/outputs"
    )
    src_dir = os.path.join(settings.MEDIA_ROOT, base_rel, fmt)
    zip_base = os.path.join(settings.MEDIA_ROOT, base_rel, f"{fmt}_output")
    zip_path = zip_base + ".zip"

    if not os.path.isdir(src_dir):
        logger.warning("download_data: missing output dir %s", src_dir)
        return JsonResponse({"error": "output dir missing", "file": ""}, status=404)

    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        shutil.make_archive(zip_base, "zip", src_dir)
    except Exception as e:
        logger.exception("download_data: zip failed for %s", src_dir)
        return JsonResponse({"error": str(e), "file": ""}, status=500)

    # rstrip prevents the '/medias//workspaces/...' double slash in your log
    url_file = f"{settings.MEDIA_URL.rstrip('/')}/{base_rel}/{fmt}_output.zip"
    return JsonResponse({"file": url_file})
    

@csrf_exempt
def process_data_form(request):
    print("### REQUEST SUBMITTED ###")
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

    print(f"# TIMESTEP: {time_step}")
    
    thread1 = produce_grid(workspace, udata, cellsize=udata.cell_size)
    thread1.join()
    print("#### GRID PRODUCED ####")
    thread2 = produce_neighbourhood(workspace, udata, spedStrg=udata.cell_size)
    thread2.join()
    print("#### NEIGHBOURHOOD PRODUCED ####")
    thread3 = run_model(constraints, duration=duration, start_month=start_month, 
                       start_year=start_year, time_step=time_step, workspace=workspace, udata=udata)
    thread3.join()
    print("#### MODEL RUN COMPLETED PRODUCED ####")
    return JsonResponse({
        "success": "ok",
    })
