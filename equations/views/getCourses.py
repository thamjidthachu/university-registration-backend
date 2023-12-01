import cx_Oracle
from django.conf import settings
from rest_framework.generics import GenericAPIView
from django.http import HttpResponse
from equations.models.courses import UniversirtyCourse
from registration.scripts.oracle import Oracle

import logging
logger = logging.getLogger('root')


class GetUniversityCourses(GenericAPIView):
    """
    Aim of this function to get all university courses data
    and insert it to database
    """

    def get(self, request):

        cur = Oracle()
        query = """
        select course_no,course_code_s,course_code,course_name_s,course_name,crd_hrs,faculty_no from mcst.sis_courses
        """
        course_data = cur.select(query)
        if not isinstance(course_data, list):
            logger.info(f"Error when Fetching schools {course_data}")
            return False

        for course in course_data:
            try:
                UniversirtyCourse.objects.create(
                    course_no=course[0],
                    code=course[1],
                    arabic_code=course[2],
                    name=course[3],
                    arabic_name=course[4],
                    hours=course[5],
                    faculty=course[6]
                )
            except Exception as e:
                logger.info(f"[EXCEPTION][GET_COURSES]: {e}")
                continue
        return HttpResponse('Courses Added successfully')
