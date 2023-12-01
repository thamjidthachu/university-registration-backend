import logging

from django.db import transaction, DatabaseError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from email_handling.views.body_mails import registerMail
from registration.serializers.user.registerSerializer import RegisterSerializer
from registration.serializers.user.uploadSerializer import RegisterUploadFilesSerializer
from registration.tasks import send_email, saved_oracle_process

logger = logging.getLogger('registration')


class Register(GenericAPIView):
    serializer_class = RegisterSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            register = RegisterSerializer(data=self.request.data, context={'request': self.request})
            register.is_valid(raise_exception=True)
            if 'area_code' in self.request.data:
                register.validated_data['area_code'] = self.request.data['area_code']
            applicant = register.create(register.validated_data)
            for field_name, uploaded_file in self.request.FILES.items():
                files = RegisterUploadFilesSerializer(data={
                    "file_name": field_name,
                    "url": uploaded_file,
                    "gender": applicant.gender,
                    "applicant_id": applicant.id
                })
                files.is_valid(raise_exception=True)
                files.create(files.validated_data)

            saved_oracle_process.delay(applicant.id, applicant.email, applicant.national_id, 1)
            saved_oracle_process.delay(applicant.id, applicant.email, applicant.national_id, 4)

            body = registerMail()
            send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                             applicant.email, applicant.arabic_first_name, applicant.gender,
                             english=body['english'], arabic=body['arabic'],
                             subject='Al Maarefa University Registration succeeded', link="Login Now")
            return Response(register.data, status=HTTP_200_OK)
        except DatabaseError as e:
            logger.debug(f"""[REGISTRATION][DATABASE][EXCEPTION]: Error Occurred while Registering, Exception - {e},
                         Register Data - {self.request.data}, Status: All Transaction Has Rolled Back""")
            return Response({"exception": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
