
from django.urls import path
from .views import *

app_name="authentication"
urlpatterns=[
    path('', home, name="home"),
    path('register/'  , register  , name="register"),
    path('login/', user_login, name="user_login"),
    path('logout/', logout_user, name="logout_user"),
    path('password_reset/', password_reset, name="password_reset")
]