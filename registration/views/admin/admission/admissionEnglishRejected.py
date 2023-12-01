import ast

from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from email_handling.views.body_mails import englishCertifiedNotVerifiedMail, englishCertifiedFailedMail
from registration.models.applicant import Applicant, Files
from registration.models.system_log import SystemLog
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.SytemLogs import SystemLogsSerializer
from registration.serializers.admin.admissionSerializer import ApplicantRejectedRetrieveSerializer
from registration.serializers.admin.englishGradeSerializer import EnglishCertificateListSerializer, \
    EnglishCertificateResultSerializer
from registration.serializers.user.uploadSerializer import UpdateOtherFilesSerializer, UpdateEnglishFilesSerializer, \
    EnglishCertificateFileSerializer
from registration.tasks import send_email


class EnglishCertificateRejected(GenericAPIView):
    pagination_class = ApplicantListPagination()

    def get(self, request, *args, **kwargs):
        applicant_id = self.request.query_params.get('applicant_id', None)
        if applicant_id:
            applicant = self.get_applicant(applicant_id)
            response = {
                "applicant": ApplicantRejectedRetrieveSerializer(applicant).data,
                'file': None,
                'old_logs': None,
                'old_file': None,
            }
            old = SystemLog.objects.filter(modified_to__startswith=applicant.full_name, before_modified__contains='english_certificate_score').last()
            if old:
                response['old_logs'] = ast.literal_eval(SystemLogsSerializer(old).data['before_modified'])

            file = Files.objects.filter(applicant_id=applicant_id, file_name__in=['academic_ielts', 'step', 'english_certf', 'tofel'])
            if file.exists():
                response['file'] = EnglishCertificateFileSerializer(file, many=True).data
            old_file = Files.objects.filter(applicant_id=applicant_id, file_name__istartswith='old')
            if old_file.exists():
                response['old_file'] = EnglishCertificateFileSerializer(old_file, many=True).data
            return Response(response, status=HTTP_200_OK)

        state = self.request.query_params.get('state', None)
        major = self.request.query_params.get('major', None)
        semester = self.request.query_params.get('semester', None)

        applicants = self.get_applicants(state, major, semester)

        query = self.request.query_params.get('query')
        if query not in ["", None]:
            applicants = applicants.filter(
                Q(arabic_full_name__istartswith=query) | Q(full_name__istartswith=query) | Q(email__istartswith=query) |
                Q(national_id__istartswith=query) | Q(arabic_last_name__icontains=query) | Q(last_name__icontains=query)
            ).order_by("-registration_date")

        if applicants is None or applicants.count() <= 0:
            return Response({"warning": "No applicants Found", "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        query = self.pagination_class.paginate_queryset(applicants, self.request)

        return self.pagination_class.get_paginated_response(EnglishCertificateListSerializer(query, many=True).data)

    def put(self, request, *args, **kwargs):
        try:
            applicant_id = int(self.request.data['id'])
            user_id = int(self.request.session['user']['pk'])
            english = EnglishCertificateResultSerializer(data=self.request.data)
            english.is_valid(raise_exception=True)
            applicant = self.get_applicant(applicant_id)
            english.validated_data['user'] = self.get_user(user_id)
            english.update(applicant, english.validated_data)
            file = self.get_file(applicant_id, request.data.get('test_type', None))
            if file:
                data = UpdateOtherFilesSerializer(data={
                    "file_name": request.data.get('test_type', None),
                    "url": request.data['url'] if 'url' in request.data else None,
                    "user": user_id
                })
                data.is_valid(raise_exception=True)
                data.update(file, data.validated_data)
            elif self.request.FILES.items():
                data = UpdateEnglishFilesSerializer(data={
                    "file_name": request.data.get('test_type', None),
                    "url": request.data.get('url', None),
                    "applicant_id": applicant_id,
                    "user": user_id
                })
                data.is_valid(raise_exception=True)
                data.create(data.validated_data)

            if english.validated_data['english_certf_result'] == "L":
                body = englishCertifiedNotVerifiedMail()
                send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                                 applicant.email, applicant.arabic_first_name, applicant.gender,
                                 english=body['english'],
                                 arabic=body['arabic'],
                                 subject='Al Maarefa University English Certificate Result', link="الدخول لحسابك")

            elif english.validated_data['english_certf_result'] in ["F", "U"]:
                body = englishCertifiedFailedMail()
                send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                                 applicant.email, applicant.arabic_first_name, applicant.gender,
                                 english=body['english'],
                                 arabic=body['arabic'],
                                 subject='Al Maarefa University English Certificate Result', link="الدخول لحسابك")

            return Response("Done", status=HTTP_200_OK)
        except Exception as e:
            return Response({"Exception": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def get_applicants(self, state, major, semester):
        query_set = Applicant.objects.filter(
            apply_semester=semester, english_certf_result__isnull=False, english_certf_result__in=["F", "L"],
        ).exclude(major_id__name='NM').order_by("-registration_date")

        if state not in ["all", "", None]:
            query_set = query_set.filter(english_certf_result=self.get_result_filter(state))
        if major not in ["all", "", None]:
            query_set = query_set.filter(major_id__name=major)

        return query_set

    @staticmethod
    def get_result_filter(state):
        result = {
            "failed": "F",
            "low_score": "L",
        }
        if state in result:
            return result[state]

        return -1

    @staticmethod
    def get_user(user_id):
        return User.objects.get(id=user_id)

    @staticmethod
    def get_applicant(applicant_id):
        return Applicant.objects.get(id=applicant_id)

    @staticmethod
    def get_file(applicant_id, file_type):
        try:
            return Files.objects.get(applicant_id=applicant_id, file_name=file_type)
        except:
            return False
