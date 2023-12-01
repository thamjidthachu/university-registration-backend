from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from registration.models.applicant import Applicant, Files
from registration.models.user_model import User
from registration.serializers.admin.admissionSerializer import ApplicantRetreiveSerializer
from registration.serializers.user.uploadSerializer import AdmissionFileUploadSerializer, ReUploadSerializer


def get_applicants(semester):
    return Applicant.objects.filter(init_state__isnull=True, apply_semester=semester)


class AdmissionFileUpload(GenericAPIView):

    def get(self, request, *args, **kwargs):
        applicants = ApplicantRetreiveSerializer(get_applicants(self.request.query_params['semester']), many=True).data

        if not applicants:
            return Response({"warning": "No applicants Found",
                             "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        return Response({"applicants": applicants}, status=HTTP_200_OK)

    def post(self, *args, **kwargs):
        applicant = Applicant.objects.get(id=self.request.query_params.get('id', None))
        for field_name, uploaded_file in self.request.FILES.items():
            files = AdmissionFileUploadSerializer(data={
                "file_name": field_name,
                "url": uploaded_file,
                "applicant_id": applicant.id
            })
            files.is_valid(raise_exception=True)
            files.create(files.validated_data)
        return Response("Done", status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        try:
            applicant_id = self.request.data['applicant_id']
            for file_name, uploaded_file in self.request.FILES.items():
                data = {
                    "file_name": file_name,
                    "url": uploaded_file
                }
                re_upload = ReUploadSerializer(data=data)
                re_upload.is_valid(raise_exception=True)
                try:
                    app = Files.objects.get(applicant_id=applicant_id, file_name=file_name)
                except Exception as e:
                    return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
                re_upload.update(app, re_upload.validated_data)
            return Response({"success": "Success"}, status=HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
