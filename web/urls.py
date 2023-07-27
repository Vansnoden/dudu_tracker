
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('process_form/', process_data_form, name="process_form"),
    path('get_result/<int:index>', get_outputs, name="get_outputs")
]
