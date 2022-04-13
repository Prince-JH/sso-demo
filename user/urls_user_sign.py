from django.urls import path
from .views import *
# from .views_user_sign import UserSign, activate
from .views_test import *
from .views_user_sign import *

urlpatterns = [

    path('sign-in', UserSign.as_view({"post": "sign_in"}), name="sign-in"),
    path('sign-up', UserSign.as_view({"post": "sign_up"}), name="sign-up"),
    path('test', test, name="test"),
]