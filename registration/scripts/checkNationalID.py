from .oracle import Oracle
import logging
from django.conf import settings

logger_oracle = logging.getLogger('root')
logger = logging.getLogger('root')


def check_national_id(national_id):
    """
        this class is checked the national id that given from new applicant is already in E-register or not
    """

    cur = Oracle()
    _view = settings.ORACLE
    result = cur.select(f'''SELECT COUNT(*) FROM {_view}.SIS_APPLICATIONS WHERE NATIONAL_ID=:NATIONAL_ID''',
                        NATIONAL_ID=national_id)

    if len(result) > 0:
        return True

    message = f"[CHECK-STUDENT-ID] check student id exception" + \
              f" with national id {national_id} and " + \
              f"failure is {result}"

    logger_oracle.exception(message)
    return False
