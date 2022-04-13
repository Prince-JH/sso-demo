import base64
import json
import traceback

import boto3
import requests as requests
import simplejson as simplejson
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cognito.modules import *
from common.func import rtn_rsp
from common.globals import *


@api_view(['POST'])
@permission_classes([AllowAny])
def test(request):
    try:
        email = 'max.kim@ebridge-world.com'
        password = 'wlgns1204'
        response = cognito_sign_up_without_confirm(email, password)
        return Response(data=response, status=status.HTTP_200_OK)
    except:
        traceback.print_exc()
        return Response(data=traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)
