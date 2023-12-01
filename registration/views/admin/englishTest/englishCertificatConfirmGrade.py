from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from registration.models.applicant import Applicant, Files
from registration.serializers.admin.englishGradeSerializer import EnglishCertificateApplicantSerializer, \
    EnglishCertificateConfirmSerializer
from registration.serializers.admin.admissionSerializer import AddUserSerializer
from registration.serializers.user.uploadSerializer import EnglishCertificateFileSerializer
from email_handling.views.body_mails import englishCertificateMail
from registration.models.user_model import User
from registration.tasks import send_email


class EnglishCertificateConfirmGrade(GenericAPIView):

    def get(self, request, *args, **kwargs):
        applicant, file = self.get_applicant_file(self.request.query_params['id'])
        user_staff = AddUserSerializer(User.objects.get(email=applicant.english_grader)).data
        data = EnglishCertificateApplicantSerializer(applicant).data
        data['file'] = EnglishCertificateFileSerializer(file).data
        return Response({"data": data, "user_staff": user_staff}, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        data = self.request.data.dict()
        applicant = EnglishCertificateConfirmSerializer(data=data)
        applicant.is_valid(raise_exception=True)
        app = self.get_applicant(self.request.query_params['id'])
        applicant.update(app, applicant.validated_data)
        if applicant.validated_data['english_certf_confirmation']:
            body = englishCertificateMail(applicant)
            send_email.delay(self.request.META.get('HTTP_HOST'), app.first_name,
                             app.email, app.arabic_first_name, app.gender, english=body['english'],
                             arabic=body['arabic'],
                             subject='Al Maarefa University KSA English Certificate Result', link="الدخول لحسابك")

        return Response("Done", status=HTTP_200_OK)

    @staticmethod
    def get_applicant_file(applicant_id):
        return Applicant.objects.get(id=applicant_id), Files.objects.filter(applicant_id=applicant_id, file_name__in=['academic_ielts', 'step', 'english_certf', 'tofel']).first()

    @staticmethod
    def get_applicant(applicant_id):
        return Applicant.objects.get(id=applicant_id)

    @staticmethod
    def get_user(user_id):
        return User.objects.get(id=user_id)
