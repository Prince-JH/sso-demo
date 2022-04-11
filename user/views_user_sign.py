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
from common.globals import *
from user.models import Member

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
                                            'msg': openapi.Schema(type=openapi.TYPE_STRING)
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
                email = request.data.get('email').strip
                password = request.data.get('password')
                first_name = request.data.get('first_name', '')
                last_name = request.data.get('last_name', '')
                nickname = request.data.get('nickname', '')
                language_code = request.data.get('language_code', 'en')
                time_zone = request.data.get('time_zone', '')
                country_code = request.data.get('nationality_country_code', '')

                # 중복 이메일 확인
                if Member.objects.filter(email=email, lc_status=STATUS_ACTIVE).count() > 0:
                    return Response(data={'msg': '이미 존재하는 이메일입니다.'}, status=status.HTTP_200_OK)

                # Cognito 저장
                if cognito_sign_up_without_confirm(username=email, password=password):
                     # DB 저장
                    Member.objects.create(
                        email=email,
                        nickname=nickname,
                        is_staff=False,
                        date_joined=timezone.now()
                    )
                # Cognito 저장 실패
                else:
                    return Response(data={'msg': 'Cognito Error'}, status=status.HTTP_200_OK)

                # Cognito Sign in
                sign_in_res = cognito_sign_in(email, password)
                if sign_in_res:
                    access_token = ['AuthenticationResult']['AccessToken']
                    refresh_token = ['AuthenticationResult']['RefreshToken']


                # 인증 확인
                user = User.objects.filter(email=email, verification=STATUS_COMPLETE)
                if len(user) > 0:
                    user = user.first()
                else:
                    result['msg'] = 'Need email verification'
                    return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                # 닉네임 중복 확인
                if user.nickname != STATUS_COMPLETE:
                    result['msg'] = 'Need duplicate nickname check'
                    return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

                user.last_login = timezone.now()
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.nickname = nickname
                user.save()

                user_profile = UserProfile.objects.get(user=user, lc_status=STATUS_ACTIVE)
                user_profile.signup_source = system
                user_profile.language_code = language_code
                user_profile.time_zone = time_zone
                user_profile.nationality_country_code = Country.objects.get(country_code=country_code).country_code
                user_profile.save()

                # return rtn_rsp(data=result, data_code=RESPONSE_SUCCESS, status_code=status.HTTP_200_OK)

        except:
            logger.debug(f'v2/users/sign-up: {traceback.format_exc()}')
            return rtn_rsp(data={"error": traceback.format_exc()}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description='[김지훈] 회원가입 메일인증',
        operation_summary="[김지훈] 회원가입 메일인증",
        operation_id='회원가입_02',
        tags=['얄리얄리_회원가입'],
        manual_parameters=[verification, verification_code, language],
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
                                            'msg': openapi.Schema(type=openapi.TYPE_STRING),
                                            'verification': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                            'time': openapi.Schema(type=openapi.TYPE_INTEGER)
                                        })
                                }
                                )})
    def email_verify(self, request):
        try:
            logger.debug(f'v2/users/email-verification')
            logger.debug(f'method: post')
            logger.debug(f'request_data: {request.data}')
            logger.debug(f'request_query_param: {request.GET}')

            result = dict()
            result['msg'] = ''
            verification = request.GET.get('verification', '')
            data = request.data
            email = data.get('email')

            # 이메일 유효성 검사
            domain = email.split('@')[1].split('.')[0]
            if domain in INVALID_EMAIL:
                result['msg'] = 'Invalid Email'
                return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)

            if verification == '':
                return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_400_BAD_REQUEST)

            # 이메일 전송
            elif verification == 'transmit':
                old_users = User.objects.filter(email=email)
                if old_users.count() > 0:
                    if old_users.filter(lc_status=STATUS_ACTIVE).count() > 0:
                        result['msg'] = 'This email already exists'
                        return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_200_OK)
                    else:
                        # 기존의 pre_save 된 계정 delete
                        old_users.delete()

                lang_code = request.GET.get('language', 'en')
                verification_code = random.randrange(100000, 1000000)
                user = User.pre_save(verification_code, email)

                result['verification'] = True
                # 인증 유효시간 180초
                result['time'] = VERIFICATION_TIME

                if settings.DEPLOY_SERVER_TYPE != 'test':
                    send_verification_email_v2(email, YALLIYALLI, lang_code, verification_code)
                # user.verify_email(verification_code)
                data_code = RESPONSE_SUCCESS

            # 인증 확인
            elif verification == 'confirm':

                verification_code = request.GET.get('verification_code', '')
                if verification_code == '':
                    return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_400_BAD_REQUEST)

                user = User.objects.get(email=email)

                # 유효 시간 180초
                if user.lc_start_date + timedelta(seconds=VERIFICATION_TIME) <= timezone.now():
                    result['msg'] = 'Time out'
                    correct = False
                    data_code = RESPONSE_FAIL

                else:
                    if user.verification == verification_code:
                        user.verification = STATUS_COMPLETE
                        user.save()
                        correct = True
                        data_code = RESPONSE_SUCCESS
                        return redirect('https://yalliyalli.com/en/main/')

                    else:
                        result['msg'] = 'Wrong code'
                        correct = False
                        data_code = RESPONSE_FAIL

                result['verification'] = correct
                result['time'] = 0
            return rtn_rsp(data=result, data_code=data_code, status_code=status.HTTP_200_OK)
        except:
            logger.debug(f'v2/users/email-verification: {traceback.format_exc()}')
            traceback.print_exc()
            return rtn_rsp({"error": traceback.format_exc()}, data_code=RESPONSE_FAIL,
                           status_code=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description='[김지훈] 회원가입 닉네임 중복 화인',
        operation_summary="[김지훈] 회원가입 닉네임 중복 확인",
        operation_id='회원가입_03',
        tags=['얄리얄리_회원가입'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING)
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
    def check_duplicate_nickname(self, request):
        try:
            logger.debug(f'v2/users/nickname/duplicate')
            logger.debug(f'method: post')
            logger.debug(f'request_data: {request.data}')
            logger.debug(f'request_query_param: {request.GET}')

            result = dict()
            result['msg'] = ''
            data = request.data
            nickname = data.get('nickname', '')

            if nickname == '':
                result['msg'] = 'No input'
                return rtn_rsp(data=result, data_code=RESPONSE_FAIL, status_code=status.HTTP_400_BAD_REQUEST)

            # 중복 검사
            else:
                data_code = RESPONSE_FAIL if User.objects.filter(lc_status=STATUS_ACTIVE,
                                                                 nickname=nickname).count() > 0 else RESPONSE_SUCCESS

            return rtn_rsp(data=result, data_code=data_code, status_code=status.HTTP_200_OK)
        except:
            logger.debug(f'v2/users/nickname/duplicate: {traceback.format_exc()}')
            traceback.print_exc()
            return rtn_rsp({"error": traceback.format_exc()}, data_code=RESPONSE_FAIL,
                           status_code=status.HTTP_400_BAD_REQUEST)


# 계정 활성화 함수
@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, email):
    logger.debug(f'v2/users/email-verification/<email>')
    logger.debug(f'method: get')
    logger.debug(f'request_data: {request.data}')
    logger.debug(f'request_query_param: {request.GET}')
    verification_code = request.GET.get('verification_code', '')

    try:
        user = User.objects.get(email=email)
    except(TypeError, ValueError, OverflowError, User.DoesNotExsit):
        user = None
    if user is not None:

        # 유효 시간 600초
        # 인증 시간 만료
        if user.lc_start_date + timedelta(seconds=VERIFICATION_TIME) <= timezone.now():
            return render(request, 'email/test.html', {'message': 'invalid'})

        else:
            # 인증 성공
            if user.verification == verification_code:
                user.verification = STATUS_COMPLETE
                user.save()
                return render(request, 'email/test.html', {'message': 'invalid'})
                # return redirect('https://yalliyalli.com/en/main/')

            # 인증 메일 만료(재시도 했음)
            else:
                return render(request, 'email/test.html', {'message': 'invalid'})
