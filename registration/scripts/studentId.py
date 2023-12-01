from registration.models.applicant import Applicant
from registration.scripts.oracle import Oracle
from django.conf import settings
import logging

logger_oracle = logging.getLogger('root')
logger = logging.getLogger('root')


def getStudentID(DB=settings.ORACLE):
    cur = Oracle()
    data = cur.select(
        f"SELECT NATIONAL_ID, STUDENT_ID FROM {DB}.SIS_APPLICATIONS where STUDENT_ID IS NOT NULL AND SEMESTER={settings.CURRENT_SEMESTER}")
    ids_applicants = []
    for item in data:
        app = Applicant.objects.filter(national_id=item[0], student_id__isnull=True, apply_semester=str(settings.CURRENT_SEMESTER))
        if app.exists():
            app = app.last()
            app.student_id = item[1]
            app.save()
            ids_applicants.append(app)
            message = f"[GET-STUDENT_ID] The applicant with national id {app.national_id} has been added the student id {item[1]}"
            logger.debug(message)

    cur.close_connection()

    return ids_applicants
