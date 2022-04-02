import traceback

import boto3

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up_without_confirm(request):
    try:
        # username = 'temp'
        print("cognito_sign_up_without_confirm")
        username = 'max.kim@ebridge-world.com'
        password = 'wlgns1234'

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_AWS_REGION)
        response = client.sign_up(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            Username=username,
            Password=password,
            MessageAction='SUPPRESS'
        )

        print(response)
        return Response(data=response, status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_200_OK)
    except:
        traceback.print_exc()
        return Response(data=traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up_with_confirm(request):
    try:
        # username = 'temp'
        print("cognito_sign_up_with_confirm")
        username = 'max.kim@ebridge-world.com'
        password = 'wlgns1234'

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_AWS_REGION)
        response = client.admin_create_user(
            UserPoolId=settings.COGNITO_AWS_USER_POOL,
            Username=username,
            TemporaryPassword=password,
        )

        print(response)
        return Response(data=response, status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_200_OK)
    except:
        traceback.print_exc()
        return Response(data=traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_sign_up(request):
    try:
        # username = 'temp'
        print("cognito_confirm_sign_up")
        username = 'alahoon@naver.com'
        confirm_code = '542773'

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_AWS_REGION)
        response = client.confirm_sign_up(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            Username=username,
            ConfirmationCode=confirm_code,
        )

        print(response)
        return Response(data=response, status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_200_OK)
    except:
        traceback.print_exc()
        return Response(data=traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_in(request):
    try:
        print("cognito_sign_in")
        username = 'max.kim@ebridge-world.com'
        password = 'wlgns1234'

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_AWS_REGION)
        response = client.initiate_auth(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': username, 'PASSWORD': password}
        )

        print(response)
        return Response(data=response, status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_200_OK)
    except:
        traceback.print_exc()
        return Response(data=traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_access_token(request):
    try:
        print("cognito_get_access_token_by_refresh_token")
        refresh_token = 'eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.FBsaaiazOyM-CnakonU0xrbpoQbxwO2' \
                        'g3VW0qOmZkiMcbl3g8eJuTva5nv2H37uWRnATZIm16q4NpTuzbo8iwQq8poUDFPRy6kZN5bl67PoSVgF4eDHkEr1RHR_wg' \
                        'OVTjVPDLu3UbwFQoMyQ-RNeBZ74Udvjw-4fAOZevAL8Y7Oa-flrWNS7dsLfY9Cw8cPKGKako9u61RqGjg3dmMjHSlUof-' \
                        'vgzo0swaCE2AucMqIP5UeEYXnRUSxsWIjU4a6XYjLntVlRnm00Zpf_ZTWR77ddVUNx38WMX0SralbGU1HtDiVHZM0YgiQ3' \
                        'VZVRFQl2FTFznk7go-SFAzJ-Mmwarw.HK_GO7fhR7wRoPsF.QST_hievMSd08ycEp5cegmA-bqCOAQPGd1ODLexHG5tCX-' \
                        'I3iVqr9zNzh1j3W3pUwKnoh18PQmqYj9SaKEyqh0EsTtUzYbrxiXrL9y5Z6k2eoVaYEHU8nzw_0UbrtwTwFAxn3eHo470Pb' \
                        '8LLtDXoWXmTDSsC9tsXObjwEgSxsmeuoH9smc2qJEfYS0xe9ymYUMiNfK4lk7yqR2gf2AiYLa98nqYAwzzOU-D2ow0hlng' \
                        '-5ny9FxJb8LRQjBmmWHIaTWitqcg9P0l5KoqzWIGZmDL4uG-rvcugTSVyUC-XbRL4j6KjTiDVT5TeBZj31Tidlsy2IKquBD' \
                        'Cht4XcTNJsH9hUE-0yBZsDu4_CVIl3nh1TmANq5DnEHuoZz1c8VT0dJKUCawLSjw5JgaejjjntXNR56Xhifjf3H-xh3IGbC' \
                        'kS6sXy2R4vdzDZCzX_ODImImJ_QPxI0RtvFJ4fJuydzOdt3PCmXE45vd6OPA_cyryEPKVNm9CP6pJqUkejxgzNrGdKWjNdI' \
                        'wuC64gm4Um8Sj5Fc1g3we13wzhJ58wDd6MEk_gnkf6ETnkXkizHL8b6PgREfDHzJrlZPW_9E13ajr8rZEWLrX-628qSPkF' \
                        '5J0MPyXPceaohsxFUo1QRq4VREMP5Wh_KJc8xSicTD2b88zpwvyjWHW8f4jjR63g7NbI7ynya-VIhtrvQBFWFzaKgzbyWvl' \
                        'GaDqFogq1rzsWFuyATTGV7CPs7YcPua13dOX-IuqlECGg9KqZEVLDRUqbTX2EkjYXIiF19kvRCg0t4QNN6uBz5gBg-qk8n' \
                        'VJGMoijZpLYAobcfbnqUzlakeTtbbjkP16VvpDcBHVOeCAzMiRZeBetPmJ-Z5_a5rpmlwnG6x2xRa6bES1_ORfauBHmztn9' \
                        'EF_RM_ymLiSmMr2lrw4-adbWJiZHhDlHeGoyf2DEJnGnK1yW8jyFx21vURm2DPOfbC5mWOZvlRNhz6gpfXxC7m_jsdlpdIF' \
                        'lA8CYEmSxCbKJWD0Ahb4td5NFEtQ0r_GtqVr0njs1pbd89k4E1MjyEZ3jekDrzgYJFnqZd7499YKI6qZmW2gAz4pVKpc8w8' \
                        'm7KPRv4_bMXdITuCoQPP9D7Z3X-nvM8VcR4piyLO24tr8PXgmYA0Nbsr5iFP42mq7e78XHdhEkQexWBk6NOoxFYE9hOXC8-' \
                        'wfX5cpn-7V9BILLoBHkUp9wxS2BTEXDIxIVoKuVfAwWY-SzHjy_LowBq0_UfX_ztKS7nx9EOV-i0HLCdgTs8NadvnIxYfOa' \
                        '0t1r5qsmR6_Bady4NBUstg1tKiAuumuUdLye8uiKby-zgAJhAsXnGQpEF4ZCriO9bOLVQWQQgKRLg2.h9u_Ez4FF9_EqgW1a2q23g'

        client = boto3.client('cognito-idp', region_name=settings.COGNITO_AWS_REGION)
        response = client.initiate_auth(
            ClientId=settings.COGNITO_YY_DEV_CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={'REFRESH_TOKEN': refresh_token}
        )

        print(response)
        return Response(data=response, status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_200_OK)
    except:
        traceback.print_exc()
        return Response(data=traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)


