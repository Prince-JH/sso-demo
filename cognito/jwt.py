from jwt.algorithms import RSAAlgorithm
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate

import jwt

# Cognito token decoder
"""
cognito 에서 제공하는 기본 정보를 가져오는 함수
sub id, email 등 해당 토큰을 받아 user 로그인 또는 user 생성 모듈에 관련 정보를 전달
디코드 하는 과정에서 settings.py 에서 설정한 Decode API Url에 유효하지 않은 토큰이 전달될 경우 에러 발생
"""
def cognito_jwt_decoder(token):
    options = {'verify_exp': api_settings.JWT_VERIFY_EXPIRATION}
    # JWT  토큰을 decode 함
    unverified_header = jwt.get_unverified_header(token)
    print("unverified_header:", unverified_header)
    if 'kid' not in unverified_header:
        raise jwt.DecodeError('Incorrect Authentication credentials')

    kid = unverified_header['kid']
    print("kid:", kid)
    try:
        public_key = RSAAlgorithm.from_jwk(api_settings.JWT_PUBLIC_KEY[kid])
    except KeyError:
        raise jwt.DecodeError('Can\'t find Proper public key in jwks')
    else:
        decoded_token = jwt.decode(
            token,
            public_key,
            api_settings.JWT_VERIFY,
            options=options,
            leeway=api_settings.JWT_LEEWAY,
            audience=api_settings.JWT_AUDIENCE,
            issuer=api_settings.JWT_ISSUER,
            algorithms=[api_settings.JWT_ALGORITHM]
        )
        return decoded_token

"""
cognito 에서 전달받은 토큰이 유효하다면, 아래 함수를 실행하여 로그인 또는 유저 생성
장고 내부 함수인 authenticate 에 유저 관련 정보를 넘기게 되면, django 에서 요청받는 토큰에 대해 user 객체 생성
payload 에서는 decode한 토큰의 정보를 가져오고, 토큰 정보(cognito에서 생성한 유저 정보)에서 sub_id만 가져옴
"""
def user_info_handler(payload):
    username = payload.get('sub')
    authenticate(remote_user=username)
    return username