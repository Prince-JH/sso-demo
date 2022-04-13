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


class UserSign(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    language = openapi.Parameter(
        'language',
        openapi.IN_QUERY,
        description='사용 언어: en, zh, ja, uz, vi, th',
        type=openapi.TYPE_STRING
    )
    permission_classes = [AllowAny]

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='[김지훈] 회원가입',
        operation_summary="[김지훈] 회원가입",
        operation_id='회원가입_01',
        tags=['유저서비스_회원가입'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'system': openapi.Schema(type=openapi.TYPE_STRING, example='yalliyalli_web'),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'time_zone': openapi.Schema(type=openapi.TYPE_STRING),
                'nationality_country_code': openapi.Schema(type=openapi.TYPE_STRING)
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
                                            'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                            'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
                                        })
                                }
                                )})
    # Todo test code 작성
    def sign_up(self, request):
        logger.debug(f'v2/users/sign-up')
        logger.debug(f'method: post')
        logger.debug(f'request_data: {request.data}')
        logger.debug(f'request_query_param: {request.GET}')
        try:
            with transaction.atomic():

                result = dict()
                result['msg'] = ''

                system = request.data.get('system', '')
                email = request.data.get('email')
                password = request.data.get('password')
                nickname = request.data.get('nickname', '')
                language_code = request.data.get('language_code', 'en')
                time_zone = request.data.get('time_zone', '')
                country_code = request.data.get('nationality_country_code', '')

                # 중복 이메일 확인
                if Member.objects.filter(email=email, lc_status=STATUS_ACTIVE).count() > 0:
                    return rtn_rsp(data={'msg': '이미 존재하는 이메일입니다.'}, data_code=RESPONSE_FAIL,
                                   status_code=status.HTTP_200_OK)

                # DB 저장
                member = Member.objects.create(
                    email=email,
                    nickname=nickname,
                    is_staff=False,
                    date_joined=timezone.now(),
                    language_code=language_code,
                    time_zone=time_zone,
                    country_code=country_code,
                    signup_source=system,
                    lc_status=STATUS_ACTIVE
                )
                # Cognito 저장
                if cognito_sign_up_without_confirm(email, password):
                    result['msg'] = 'Complete sign-up process by verifying your email.'
                # Cognito 저장 실패
                else:
                    return rtn_rsp(data={'msg': 'Cognito Error'}, data_code=RESPONSE_FAIL,
                                   status_code=status.HTTP_200_OK)

                # Cognito 로그인
                # access_token, refresh_token = sign_in(member, email, password)
                #
                # result['access_token'] = access_token
                # result['refresh_token'] = refresh_token

                return rtn_rsp(data=result, data_code=RESPONSE_SUCCESS, status_code=status.HTTP_200_OK)

        except:
            logger.debug(f'v2/users/sign-up: {traceback.format_exc()}')
            traceback.print_exc()
            return rtn_rsp(data={"error": traceback.format_exc()}, status_code=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description='[김지훈] 로그인',
        operation_summary="[김지훈] 로그인",
        operation_id='인증_01',
        tags=['유저서비스_인증'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING)
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
                                            'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                            'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
                                        })
                                }
                                )})
    # Todo test code 작성
    def sign_in(self, request):
        logger.debug(f'v2/users/sign-in')
        logger.debug(f'method: post')
        logger.debug(f'request_data: {request.data}')
        logger.debug(f'request_query_param: {request.GET}')
        try:
            with transaction.atomic():

                result = dict()
                result['msg'] = ''

                email = request.data.get('email')
                password = request.data.get('password')

                # YY 저장 확인
                members = Member.objects.filter(email=email, lc_status=STATUS_ACTIVE)
                if len(members) < 1:
                    return rtn_rsp(data={'msg': 'Invalid User'}, data_code=RESPONSE_FAIL,
                                   status_code=status.HTTP_200_OK)
                else:
                    member = members.first()

                # Cognito 저장 확인
                user_info = cognito_admin_get_user(email)
                # Cognito 미가입 -> 유저 migrate
                if user_info is None:
                    # Cognito 저장
                    if cognito_sign_up_with_confirm(email) and cognito_admin_set_user_password(email, password):
                        pass

                    # Cognito 저장 실패
                    else:
                        return Response(data={'msg': 'Cognito Error'}, data_code=RESPONSE_FAIL,
                                        status_code=status.HTTP_200_OK)
                # Cognito 기가입, 이메일 인증 전
                elif user_info['UserStatus'] == STATUS_UNCONFIRMED:
                    result['msg'] = 'Complete sign-up process by verifying your email.'
                    return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                # Cognito 기가입, 이메일 인증 완료
                else:
                    # Cognito 로그인
                    access_token, refresh_token = sign_in(member, email, password)
                    if access_token and refresh_token:

                        result['access_token'] = access_token
                        result['refresh_token'] = refresh_token
                    else:
                        result['msg'] = 'Invalid User Info'
                        return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                return rtn_rsp(data=result, data_code=RESPONSE_SUCCESS, status_code=status.HTTP_200_OK)

        except:
            logger.debug(f'v2/users/sign-up: {traceback.format_exc()}')
            traceback.print_exc()
            return rtn_rsp(data={"error": traceback.format_exc()}, status_code=status.HTTP_400_BAD_REQUEST)
