from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from registration.models.applicant import Applicant, Files
from registration.serializers.user.uploadSerializer import UploadSerializer, ReUploadSerializer, UploadFilesSerializer
from email_handling.views.body_mails import uploadMail
from registration.tasks import send_email


class Upload(GenericAPIView):

    def post(self, request, *args, **kwargs):
        applicant = self.get_queryset(int(self.request.session['user']['pk']))
        self.request.data['gender'] = applicant.gender
        upload = UploadSerializer(data=self.request.data)
        upload.is_valid(raise_exception=True)
        for field_name, uploaded_file in self.request.FILES.items():
            files = UploadFilesSerializer(data={
                "file_name": field_name,
                "url": uploaded_file,
                "gender": applicant.gender,
                "applicant_id": applicant.id
            })
            files.is_valid(raise_exception=True)
            files.create(files.validated_data)

        body = uploadMail()
        send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                         applicant.email, applicant.arabic_first_name, applicant.gender,
                         english=body['english'], arabic=body['arabic'],
                         subject='Al Maarefa University Initial State', link="Go to Dashboard")

        return Response({"status": applicant.init_state}, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        if len(self.request.data) > 0:

            for file in self.request.data:
                data = {
                    "file_name": file,
                    "url": self.request.data[file]
                }
                re_upload = ReUploadSerializer(data=data)
                re_upload.is_valid(raise_exception=True)
                app = Files.objects.get(applicant_id=int(self.request.session['user']['pk']),
                                        file_name=file)
                re_upload.update(app, re_upload.validated_data)

            return Response({"success": "Success"}, status=HTTP_200_OK)
        return Response({"error": "Invalid passing the data"}, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self, appId):
        return Applicant.objects.get(id=appId)
