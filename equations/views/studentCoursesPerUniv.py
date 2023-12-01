from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from equations.serializers. equivilantCoursesSerializer import ListEquivilantCoursesSerializer
from equations.models.courses import EquivalentCourse
from registration.models.applicant import Applicant
from django.db.models import Q


class StudentCoursesView(ListAPIView):

    def get(self, request):
        applicant_university = self.get_applicant_university(int(self.request.session['user']['pk']))
        if applicant_university is not None:
            result =  EquivalentCourse.objects.filter(Q(university__university_name_english__icontains=applicant_university) | Q(university__university_name_arabic__icontains=applicant_university), exception=False)
            if not result.exists():
                return Response({"warning": "No equivalent courses found for your university.",
                                 "warning_ar": "لا توجد مقررات معادلة لجامعتك."}, status=400)
            return Response(ListEquivilantCoursesSerializer(result, many=True).data)
        return Response({"warning": "No registerd university.",
                                 "warning_ar": "لا توجد جامعة مسجلة."}, status=400)

    def get_applicant_university(self, student):
        applicant = Applicant.objects.get(id=student)
        if applicant.previous_university:
            return applicant.previous_university
        return applicant.tagseer_institute