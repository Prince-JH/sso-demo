from django.contrib import admin
from django.urls import path

from sso.views_user_sign import *

urlpatterns = [
    path('api/v1/sign-up', sign_up_without_confirm, name='sign-up'),
    path('api/v1/admin-sign-up', sign_up_with_confirm, name='sign-up-with-confirm'),
    path('api/v1/sign-up/cofirmation', confirm_sign_up, name='confirm-sign-up'),
    path('api/v1/sign-in', sign_in, name='sign-in'),
    path('api/v1/refresh', refresh_access_token, name='refresh-access-token'),
]