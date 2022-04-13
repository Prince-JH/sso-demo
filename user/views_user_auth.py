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


class UserAuth(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    token_type = openapi.Parameter(
        'token_type',
        openapi.IN_QUERY,
        description='access or refresh',
        type=openapi.TYPE_STRING
    )
    permission_classes = [AllowAny]

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='[김지훈] 인증',
        operation_summary="[김지훈] 인증",
        operation_id='인증_01',
        tags=['유저서비스_인증'],
        manual_parameters=[token_type],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING)
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
                                            'msg': openapi.Schema(type=openapi.TYPE_STRING),
                                            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
                                        })
                                }
                                )})
    def authenticate(self, request):
        logger.debug(f'v2/users/authenticate')
        logger.debug(f'method: post')
        logger.debug(f'request_data: {request.data}')
        logger.debug(f'request_query_param: {request.GET}')
        try:
            with transaction.atomic():
                result = dict()
                result['msg'] = ''
                token_type = request.GET.get('token_type', 'access')
                token = request.data.get('token', '')

                # 액세스 토큰 인증
                if token_type == 'access':
                    if token == '':
                        result['msg'] = 'Require access token'
                        return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                    # 토큰 인증 성공
                    if cognito_get_user(token):
                        return rtn_rsp(data_code=RESPONSE_SUCCESS, status_code=status.HTTP_200_OK)

                    else:
                        result['msg'] = 'Expired token'
                        return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)


                # 토큰 갱신
                elif token_type == 'refresh':
                    if token == '':
                        result['msg'] = 'Require refresh_token'
                        return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                    # 토큰 갱신 성공
                    refresh_token = Token.objects.get(id=token).token
                    new_token = cognito_refresh_access_token(refresh_token)

                    if new_token:
                        result['access_token'] = new_token['AuthenticationResult']['AccessToken']
                        return rtn_rsp(data=result, data_code=RESPONSE_SUCCESS, status_code=status.HTTP_200_OK)
        except:
            logger.debug(f'v2/users/authenticate: {traceback.format_exc()}')
            traceback.print_exc()
            return rtn_rsp(data={"error": traceback.format_exc()}, status_code=status.HTTP_400_BAD_REQUEST)

