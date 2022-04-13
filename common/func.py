import importlib
import logging

from common.globals import RESPONSE_SUCCESS, RESPONSE_FAIL

logger = logging.getLogger()
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response


def rtn_rsp(data='', data_code=None, status_code=None):
    """
    3가지 케이스로 구분
    * Response 200 일떄
        - rtn_rsp(data=result, status_code=status.HTTP_200_OK)
        - rtn_rsp(data=result, data_code=RESPONSE_SUCCESS, status_code=status.HTTP_200_OK)

    * Response 400 or 500 일때
        - rtn_rsp(data=result, status_code=status.HTTP_400_BAD_REQUEST) or
          rnt_rsp(status_code=status.HTTP_400_BAD_REQUEST)
    """
    result_type = ["<class 'collections.OrderedDict'>", "<class 'collections.defaultdict'>", "<class 'dict'>",
                   "<class 'list'>"]

    if str(type(data)) not in result_type:
        data = None

    # 키/밸류 값의 스펙을 만족하면서 비즈니스 로직으로 분기되어야 하며, 상태값으로 분기되지 않는경우에는 result를 그대로 내린다.
    if status_code == 200:
        if data_code is None:
            rsp = data
            logger.debug(f'response :: {rsp}')
            return Response(data=rsp, status=status.HTTP_200_OK)

        # 키/밸류 값의 스펙을 만족하면서 비즈니스 로직으로 분기되어야 하며, 상태값으로 분기되어야 하는 경우에는 봉투패턴으로 내린다.
        elif data_code in [RESPONSE_SUCCESS, RESPONSE_FAIL]:
            if data is None:
                data = {}

            rsp = {
                'code': data_code,
                'data': data
            }

            logger.debug(f'response :: {rsp}')
            return Response(data=rsp, status=status.HTTP_200_OK)

    # 그 외에 에러 발생시에는 400에러로 내려준다
    elif status_code == 400:
        rsp = str(data)
        logger.debug(f'response :: {rsp}')
        return Response(data=rsp, status=status.HTTP_400_BAD_REQUEST)

    else:
        if data is not None:
            rsp = data
        else:
            rsp = None
        logger.debug(f'response :: {rsp}')
        return Response(data=rsp, status=status_code)