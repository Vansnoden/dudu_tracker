from django.shortcuts import render

# Create your views here.

MONTHS = [
    "Jan","Feb","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"
]

TSTEPS = [
    "Monthly", "Yearly"
]

def home(request):
    return render(request, "web/index.html", {
        "months": MONTHS,
        "tsteps": TSTEPS
    })