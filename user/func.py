from cognito.modules import cognito_sign_in
from common.globals import *
from user.models import Token


def sign_in(member, email, password):
    sign_in_res = cognito_sign_in(email, password)
    if sign_in_res:
        access_token = sign_in_res['AuthenticationResult']['AccessToken']
        refresh_token = sign_in_res['AuthenticationResult']['RefreshToken']

        # Refresh 토큰 저장 or 변경
        tokens = Token.objects.filter(member=member, lc_status=STATUS_ACTIVE)
        if len(tokens) > 0:
            token = tokens.first()
            token.token = refresh_token
            token.save()
        else:
            token = Token.create_token(member, refresh_token)

        # Refresh 토큰의 id 응답
        return access_token, token.pk

    else:
        return None, None
