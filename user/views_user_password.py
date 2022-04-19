import importlib
import logging
import operator
import json
import random
import traceback
from datetime import timedelta
from email.utils import parseaddr

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.views import View
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from cognito.modules import *
from common.func import rtn_rsp
from common.globals import *
from user.func import sign_in
from user.models import Member, Token

logger = logging.getLogger()
import requests
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Min
from django.db import transaction
from collections import OrderedDict
from rest_framework import status, viewsets, mixins, permissions


class UserPassword(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    token_type = openapi.Parameter(
        'token_type',
        openapi.IN_QUERY,
        description='access or refresh',
        type=openapi.TYPE_STRING
    )
    permission_classes = [AllowAny]

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='[김지훈] 비밀번호 변경',
        operation_summary="[김지훈] 비밀번호 변경",
        operation_id='비밀번호_01',
        tags=['유저서비스_비밀번호'],
        manual_parameters=[token_type],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING)
            }),
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT,
                                properties={
                                    'code': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        example='success'
                                    ),
                                    'data': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'msg': openapi.Schema(type=openapi.TYPE_STRING)
                                        })
                                }
                                )})
    def reset_password_send(self, request):
        logger.debug(f'v2/users/password/reset/mail')
        logger.debug(f'method: post')
        logger.debug(f'request_data: {request.data}')
        logger.debug(f'request_query_param: {request.GET}')
        try:
            with transaction.atomic():
                result = dict()
                result['msg'] = ''
                email = request.data.get('email', '')

                if email == '':
                    result['msg'] = 'Require email'
                    return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                members = Member.objects.filter(email=email)
                if len(members) == 0:
                    result['msg'] = 'Invalid email'
                    return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                member = members.first()
                headers = {
                    "Content-Type": "application/json"
                }

                url = f"{settings.UTIL_SERVER}/email"
                body = {
                    'str_subject': '[YalliYalli] Your password has been successfully reset.',
                    'str_content': 'Click the button below to change your password',
                    'html_content': 'Click the button below to change your password',
                    'list_to_address': [email],
                }
                res = requests.post(url, data=json.dumps(body), headers=headers)

                print("res:", res)

                return rtn_rsp(data=result, data_code=RESPONSE_SUCCESS, status_code=status.HTTP_200_OK)

        except:
            logger.debug(f'v2/users/authenticate: {traceback.format_exc()}')
            traceback.print_exc()
            return rtn_rsp(data={"error": traceback.format_exc()}, status_code=status.HTTP_400_BAD_REQUEST)
