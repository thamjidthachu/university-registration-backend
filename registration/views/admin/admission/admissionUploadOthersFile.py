from registration.serializers.admin.admissionSerializer import UpdateEnglishCertfSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from registration.models.applicant import Applicant, Files
from registration.serializers.user.uploadSerializer import UploadOtherFilesSerializer, UpdateOtherFilesSerializer, \
    admissionUploadEnglishFileSerializer
from registration.models.user_model import User


def get_file(id, type):
    try:
        return Files.objects.get(applicant_id=id, file_name=type)
    except:
        return False


def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return


def get_applicants(semester):
    return Applicant.objects.filter(init_state__isnull=True, apply_semester=semester)


class AdmissionOtherFileUpload(GenericAPIView):
    def put(self, request, *args, **kwargs):
        if {"id"} <= request.query_params.keys():
            user = get_user(int(request.session['user']['pk']))
            file = get_file(request.query_params.get('id'), request.data.get('type', None))
            if file:
                data = UpdateOtherFilesSerializer(data={
                    "url": request.data['url'] if 'url' in request.data else None,
                    "user": user.id
                })
                data.is_valid(raise_exception=True)
                data.update(file, data.validated_data)
                return Response("File updated Successfully", status=HTTP_200_OK)

            return Response({"error": "file not exist.",
                             "error_ar": "الملف غير موجود."}, status=HTTP_404_NOT_FOUND)

        return Response({"error": "Something wrong.",
                         "error_ar": "حدث خطأ، برجاء المحاولة مرة أخرى"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if {"id"} <= request.query_params.keys():
            applicant = Applicant.objects.get(id=self.request.query_params.get('id', None))

            file_type = request.data.get('type', None)
            if file_type == 'english':
                for field_name, uploaded_file in self.request.FILES.items():
                    file = admissionUploadEnglishFileSerializer(data={
                        "file_name": file_type,
                        "applicant_id": request.query_params['id'],
                        "url": uploaded_file
                    })
                    file.is_valid(raise_exception=True)
                    file.create(file.validated_data)
                return Response("File added Successfully", status=HTTP_200_OK)

            elif file_type in ('other', 'others', 'transcript', 'sat', 'SAT', 'gaatorsat', 'GAATORSAT'):
                for field_name, uploaded_file in self.request.FILES.items():
                    file = UploadOtherFilesSerializer(data={
                        "file_name": file_type,
                        "url": uploaded_file,
                        "applicant_id": request.query_params['id'],
                    })
                    file.is_valid(raise_exception=True)
                    file.create(file.validated_data)
                return Response("File added Successfully", status=HTTP_200_OK)
            else:
                return Response({"error": "Please select the correct choice.",
                                 "error_ar": "من فضلك تاكد من الاختيار الصحيح ثم اعد المحاولة"},
                                status=HTTP_400_BAD_REQUEST)

        return Response({"error": "Error in Connection.",
                         "error_ar": "حدث خطأ فى الأتصال"}, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if {"id"} <= request.query_params.keys():
            file = get_file(request.query_params['id'])
            if file:
                file.delete()
                return Response({"success": "File Deleted Successfully.",
                                 "success_ar": "تم حذف الملف بنجاح."}, status=HTTP_200_OK)

            return Response({"error": "file not exist.",
                             "error_ar": "الملف غير موجود."}, status=HTTP_404_NOT_FOUND)

        return Response({"error": "Something wrong.",
                         "error_ar": "حدث خطأ، برجاء المحاولة مرة أخرى"}, status=HTTP_400_BAD_REQUEST)
