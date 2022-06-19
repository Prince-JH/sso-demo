from django.urls import path
from .views import *
# from .views_user_sign import UserSign, activate
from .views_user_auth import *
from .views_user_password import *
from .views_user_sign import *

urlpatterns = [

    # user_sign
    path('sign-in', UserSign.as_view({"post": "sign_in"}), name="sign-in"),
    path('sign-up', UserSign.as_view({"post": "sign_up"}), name="sign-up"),

    # user_auth
    path('auth', UserAuth.as_view({"post": "authenticate"}), name="authenticate"),

    # user_password
    path('password/reset/mail', UserPassword.as_view({"post": "reset_password_send"}), name="authenticate"),

]