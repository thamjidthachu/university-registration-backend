from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from email_handling.views.body_mails import englishCertifiedFailedMail, englishCertifiedNotVerifiedMail
from registration.models.applicant import Applicant, Files
from registration.models.user_model import User
from registration.serializers.admin.englishGradeSerializer import EnglishCertificateApplicantSerializer, \
    EnglishCertificateResultSerializer
from registration.serializers.user.uploadSerializer import EnglishCertificateFileSerializer
from registration.tasks import send_email


class EnglishCertificateGrade(GenericAPIView):

    def get(self, request, *args, **kwargs):
        applicant, file = self.get_applicant_file(self.request.query_params['id'])
        data = EnglishCertificateApplicantSerializer(applicant).data
        data['file'] = EnglishCertificateFileSerializer(file).data
        return Response(data, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        data = self.request.data.dict()
        data['id'] = data.pop('applicant_id')
        applicant = EnglishCertificateResultSerializer(data=data)
        applicant.is_valid(raise_exception=True)
        app = self.get_applicant(self.request.query_params['id'])
        applicant.validated_data['user'] = self.get_user(int(self.request.session['user']['pk']))
        applicant.update(app, applicant.validated_data)
        if applicant.validated_data['english_certf_result'] == "L":
            body = englishCertifiedNotVerifiedMail()
            send_email.delay(self.request.META.get('HTTP_HOST'), app.first_name,
                             app.email, app.arabic_first_name, app.gender, english=body['english'],
                             arabic=body['arabic'],
                             subject='Al Maarefa University English Certificate Result', link="الدخول لحسابك")

        elif applicant.validated_data['english_certf_result'] in ["F", "U"]:
            body = englishCertifiedFailedMail()
            send_email.delay(self.request.META.get('HTTP_HOST'), app.first_name,
                             app.email, app.arabic_first_name, app.gender, english=body['english'],
                             arabic=body['arabic'],
                             subject='Al Maarefa University English Certificate Result', link="الدخول لحسابك")

        return Response("Done", status=HTTP_200_OK)

    @staticmethod
    def get_applicant_file(applicant_id):
        return Applicant.objects.get(id=applicant_id), Files.objects.filter(applicant_id__id=applicant_id, file_name__in=['academic_ielts', 'step', 'english_certf', 'tofel']).first()

    @staticmethod
    def get_applicant(applicant_id):
        return Applicant.objects.get(id=applicant_id)

    @staticmethod
    def get_user(pk):
        return User.objects.get(id=pk)
