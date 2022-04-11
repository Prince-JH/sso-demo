from django.urls import path
from .views import *
# from .views_user_sign import UserSign, activate
from .views_user_sign import UserSign

urlpatterns = [

    path('sign-in', UserSign.as_view({"post": "email_verify"}), name="sign-in"),
    path('sign-up', UserSign.as_view({"post": "email_verify"}), name="sign-up"),
]