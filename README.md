# Description

YY의 유저를 관리하는 서비스를 분리하여 추후에 추가될 마이크로 서비스에서 사용할 인증 · 인가에 대한 책임을 한 곳에서 관리하는 것을 추구합니다.
기존에 Cognito에 가입되어 있지 않던 유저들을 마이그레이션 하는 부분도 고려 대상입니다.


# Getting Started

필요 패키지 설치  
**pip install -r requirement.txt**

서버 구동
python3 manage.py runserver

swagger 주소 (8000포트 기준)
http://127.0.0.1:8000/sso-demo/swagger/

## APIs

- 인가
- 회원가입
- 로그인
- 비밀번호 변경

## User Scenario
<img width="80%" src="https://user-images.githubusercontent.com/74312505/174473720-98384f0a-4b5f-481c-8593-2276366568cf.jpg">
