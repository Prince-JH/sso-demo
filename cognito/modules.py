import traceback

import boto3

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


def cognito_sign_up_without_confirm(email, password):
    try:
        print("cognito_sign_up_without_confirm")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.sign_up(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            Username=email,
            Password=password
        )

        print("cognito_sign_up_without_confirm_response:", response)
        return response

    except:
        traceback.print_exc()
        return None


def cognito_sign_up_with_confirm(email):
    try:
        print("cognito_sign_up_with_confirm")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.admin_create_user(
            UserPoolId=settings.COGNITO_USER_POOL,
            Username=email,
            MessageAction="SUPPRESS"
        )

        print("cognito_sign_up_with_confirm_response:", response)
        return response

    except:
        traceback.print_exc()
        return None


def cognito_confirm_sign_up(email, confirm_code):
    try:
        print("cognito_confirm_sign_up")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.confirm_sign_up(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            Username=email,
            ConfirmationCode=confirm_code,
        )

        print("cognito_confirm_sign_up_response:", response)
        return response
    except:
        traceback.print_exc()
        return None

def cognito_admin_confirm_sign_up(email):
    try:
        print("cognito_admin_confirm_sign_up")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.admin_confirm_sign_up(
            Username=email,
            UserPoolId=settings.COGNITO_USER_POOL,
        )

        print("cognito_confirm_sign_up_response:", response)
        return response
    except:
        traceback.print_exc()
        return None


def cognito_sign_in(email, password):
    try:
        print("cognito_sign_in")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.initiate_auth(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': email, 'PASSWORD': password}
        )

        print("cognito_sign_in_response:", response)
        return response
    except:
        traceback.print_exc()
        return None


def cognito_refresh_access_token(refresh_token):
    try:
        print("cognito_get_access_token_by_refresh_token")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.initiate_auth(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={'REFRESH_TOKEN': refresh_token}
        )

        print("cognito_get_access_token_by_refresh_token_response:", response)
        return response
    except:
        traceback.print_exc()
        return None


def cognito_admin_set_user_password(email, new_password):
    try:
        print("cognito_admin_set_user_password")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.admin_set_user_password(
            Password=new_password,
            Permanent=True,
            Username=email,
            UserPoolId=settings.COGNITO_USER_POOL
        )

        print("cognito_admin_set_user_password_response:", response)

        return response
    except:
        traceback.print_exc()
        return None


def cognito_change_password(access_token, previous_password, new_password):
    try:
        print("cognito_change_password")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.change_password(
            AccessToken=access_token,
            PreviousPassword=previous_password,
            ProposedPassword=new_password
        )

        print("cognito_change_password_response:", response)

        return response
    except:
        traceback.print_exc()
        return None


def cognito_get_user(access_token):
    try:
        print("cognito_get_user")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.get_user(
            AccessToken=access_token
        )

        print("cognito_get_user_response:", response)
        return response
    except:
        traceback.print_exc()
        return None


def cognito_resend_email(email):
    try:
        print("cognito_resend_email")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.resend_confirmation_code(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            Username=email
        )

        print("cognito_resend_email_response:", response)
        return response
    except:
        traceback.print_exc()
        return None


def cognito_admin_get_user(email):
    try:
        print("cognito_admin_get_user")

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)
        response = client.admin_get_user(
            Username=email,
            UserPoolId=settings.COGNITO_USER_POOL
        )

        print("cognito_admin_get_user:", response)
        return response
    except:
        traceback.print_exc()
        return None
