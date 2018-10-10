from django.urls import path
app_name="user"

from apps.user.views import *

urlpatterns = [
    path('register/',register,name="register"),
    path('register_handle/',register_handle,name="register_handle"),
]