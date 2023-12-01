from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from email_handling.views.body_mails import deanMail
from registration.models.applicant import Applicant, Files
from registration.models.evaluation import EnglishTest, Interview
from registration.models.univStructure import MAJOR_CHOICES, MAJOR_CHOICES_ARABIC
from registration.models.user_model import User
from registration.serializers.admin.admissionSerializer import EnglishRetreiveSerializer
from registration.serializers.admin.deanEvalSerializer import (
    InterviewListSerializer,
    ApplicantProfileSerializer,
    FilesListSerialzer,
    EnglishListSerializer,
    ApplicantFinalUpdateSerializer,
    InterviewUpdateCertifiedSerializer
)
from registration.tasks import send_email


class deanUpdateState(GenericAPIView):

    def put(self, request, *args, **kwargs):
        if 'major' not in self.request.query_params or 'id' not in self.request.query_params:
            return Response({"error": "Sorry, Can't update data"}, status=HTTP_404_NOT_FOUND)

        user = self.get_user(int(self.request.session['user']['pk']))
        applicant = self.request.data
        app = self.get_applicant(applicant['id'],
                                 self.request.query_params['major'],
                                 faculty="PH" if user.role == 7 else "M" if user.role == 9 else "AS" if user.role == 10 else None)
        if app is None:
            return Response({"error": "No Applicant Found", "error_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        final = ApplicantFinalUpdateSerializer(data=applicant)
        final.is_valid(raise_exception=True)
        major = app.major_id.name
        final.validated_data['user'] = user
        final.validated_data['interview'] = self.get_queryset(app.id, "interview")
        final.update(app, final.validated_data)
        if final.validated_data['final_state'] in ['A', 'RJ']:
            addcertif = InterviewUpdateCertifiedSerializer(data=self.request.data)
            addcertif.is_valid(raise_exception=True)
            addcertif.update(self.get_queryset(app.id, "interview"), addcertif.validated_data)
        eng, ar = self.get_major(major)
        body = deanMail(app, eng, ar)
        send_email.delay(self.request.META.get('HTTP_HOST'), app.first_name,
                         app.email, app.arabic_first_name, app.gender, english=body['english'], arabic=body['arabic'],
                         subject='Al MAAREFA University KSA Application final review', link="الدخول لحسابك")

        return Response({"success": "Successfully"}, status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        applicant_id = self.request.query_params.get('id', None)
        major = self.request.query_params.get('major', None)
        if not (applicant_id or major):
            return Response({"error": "No Applicant Found"}, status=HTTP_404_NOT_FOUND)

        user = self.get_user(int(self.request.session['user']['pk']))
        applicant = self.get_applicant(applicant_id,
                                       major,
                                       faculty="PH" if user.role == 7 else "M" if user.role == 9 else "AS")
        if applicant is None:
            return Response({"error": "No Applicant Found"}, status=HTTP_404_NOT_FOUND)
        files = self.get_queryset(applicant.id, "files")
        english = self.get_queryset(applicant.id, "english")
        interview = self.get_queryset(applicant.id, "interview")

        applicant_profile = ApplicantProfileSerializer(applicant).data
        files_data = FilesListSerialzer(files, many=True).data
        english_data = EnglishListSerializer(english.last()).data
        english_dates = EnglishRetreiveSerializer(english, many=True).data
        english_logs = {
            "english_dates": english_dates,
            "certificate_data": None,
        }
        if self.check_english_certf(applicant):
            english_certificate_data = {
                "score": applicant.english_certf_score,
                "confirmed": applicant.english_certf_confirmation,
                "state": applicant.english_certf_result
            }
            english_logs['certificate_data'] = english_certificate_data
        interview_data = InterviewListSerializer(interview).data

        return Response({
            "profile": applicant_profile,
            "files": files_data,
            "english": english_data,
            "english_logs": english_logs,
            "interview": interview_data
        }, status=HTTP_200_OK)

    @staticmethod
    def get_queryset(applicant_id, object_type):
        try:
            if object_type == "files":
                return Files.objects.filter(applicant_id=applicant_id)
            elif object_type == "interview":
                return Interview.objects.get(applicant_id=applicant_id)
            elif object_type == "english":
                return EnglishTest.objects.filter(applicant_id=applicant_id).order_by('test_try')
        except Files.DoesNotExist or EnglishTest.DoesNotExist or Interview.DoesNotExist:
            return None

    def get_applicant(self, applicant_id, major, faculty):
        try:
            return Applicant.objects.get(id=applicant_id, major_id=major, major_id__faculty_id__name=faculty)
        except Applicant.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_major(self, major):
        m = dict(MAJOR_CHOICES)
        if major in m:
            return m[major], MAJOR_CHOICES_ARABIC[major]

    @staticmethod
    def check_english_certf(applicant):
        if isinstance(applicant.english_certf_score, float) and applicant.english_certf_score > 0:
            return True
        return False
