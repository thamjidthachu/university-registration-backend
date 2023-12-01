from rest_framework.generics import GenericAPIView
from registration.models.applicant import Applicant
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from registration.models.evaluation import EnglishTest, Interview
from registration.models.user_model import User


class RegisterInfo(GenericAPIView):
    def get(self, request, *args, **kwargs):
        if User.objects.get(pk=int(self.request.session['user']['pk'])).role == 16:
            semester = self.request.query_params.get('semester', None)
            major = self.request.query_params.get('major', None)
            data = self.get_applicant_data(semester, major)

            return Response(data, status=HTTP_200_OK)
        return Response({"error": "You don't have access.",
                         "error_ar": "ليس لديك صلاحية."}, status=HTTP_401_UNAUTHORIZED)

    @staticmethod
    def get_applicant_data(semester, major):
        applicant = Applicant.objects.all()
        english = EnglishTest.objects.all()
        interview = Interview.objects.all()
        if semester not in ['all', None, ""]:
            applicant = applicant.filter(apply_semester=semester)
            english = english.filter(applicant_id__apply_semester=semester)
            interview = interview.filter(applicant_id__apply_semester=semester)
        if major not in ['all', None, ""]:
            applicant = applicant.filter(major_id__name=major)
            english = english.filter(applicant_id__major_id__name=major)
            interview = interview.filter(applicant_id__major_id__name=major)

        data = {
            "total_applicants": applicant.count(),
            "total_female_applicants": applicant.filter(gender='F').count(),
            "total_male_applicants": applicant.filter(gender='M').count(),

            "total_english_test_applicants": english.count(),
            "total_english_test_male_applicants": english.filter(applicant_id__gender='M').count(),
            "total_english_test_female_applicants": english.filter(applicant_id__gender='F').count(),

            "total_english_test_passed_applicants": english.filter(result='S').count(),
            "total_english_test_passed_male_applicants": english.filter(result='S', applicant_id__gender='M').count(),
            "total_english_test_passed_female_applicants": english.filter(result='S', applicant_id__gender='F').count(),

            "total_english_test_failed_applicants": english.filter(result='F').count(),
            "total_english_test_failed_male_applicants": english.filter(result='F', applicant_id__gender='M').count(),
            "total_english_test_failed_female_applicants": english.filter(result='F', applicant_id__gender='F').count(),

            "total_interview_applicants": interview.count(),
            "total_interview_male_applicants": interview.filter(applicant_id__gender='M').count(),
            "total_interview_female_applicants": interview.filter(applicant_id__gender='F').count(),

            "total_interview_passed_applicants": interview.filter(result='S').count(),
            "total_interview_passed_male_applicants": interview.filter(result='S', applicant_id__gender='M').count(),
            "total_interview_passed_female_applicants": interview.filter(result='S', applicant_id__gender='F').count(),

            "total_interview_failed_applicants": interview.filter(result='F').count(),
            "total_interview_failed_male_applicants": interview.filter(result='F', applicant_id__gender='M').count(),
            "total_interview_failed_female_applicants": interview.filter(result='F', applicant_id__gender='F').count(),

            "total_student_id_generated": applicant.filter(student_id__isnull=False).count(),
            "total_male_student_id_generated": applicant.filter(student_id__isnull=False, gender='M').count(),
            "total_female_student_id_generated": applicant.filter(student_id__isnull=False, gender='F').count(),

        }

        return data
