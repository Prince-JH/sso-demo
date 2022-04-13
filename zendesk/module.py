import base64
import json
import traceback

import boto3
import requests as requests
import simplejson as simplejson
from django.conf import settings

def zendesk_sign_up(username, nickname, system='yalliyalli_web'):
    try:

        print("zendesk_sign_up")

        credentials = f'{settings.ZENDESK_ADMIN_EMAIL}:{settings.ZENDESK_ADMIN_PW}'
        encoded_credentials = str(base64.b64encode(credentials.encode("utf-8")), "utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }

        url = f"{settings.ZENDESK_URL}/api/v2/users"
        body = {
            "user": {
                "email": username,
                "name": nickname,
                "organization": {
                    "name": system
                },
                "verified": True
            }
        }
        response = requests.post(url, json.dumps(body), headers=headers)
        return response

    except:
        traceback.print_exc()
        return None
