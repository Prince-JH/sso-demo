import base64
import datetime
import json
import traceback

import boto3
import pytz
import requests as requests
import simplejson as simplejson
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cognito.modules import *
from common.func import rtn_rsp
from common.globals import *


@api_view(['GET'])
@permission_classes([AllowAny])
def test(request):
    try:
        now = datetime.datetime.today()
        print("now", now)

        time_zone = pytz.timezone("Asia/Seoul")
        local_now = time_zone.localize(now)
        print("local_now")
        print("timezone", timezone.now())
        return Response(status=status.HTTP_200_OK)
    except:
        traceback.print_exc()
        return Response(data=traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)
