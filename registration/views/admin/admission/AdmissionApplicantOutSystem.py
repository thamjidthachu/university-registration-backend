from rest_framework.generics import GenericAPIView
from registration.serializers.admin.admissionSerializer import ApplicantOutSystemSerializer
from rest_framework.response import Response
from registration.models.applicant import Applicant
from registration.models.user_model import User
from rest_framework.status import HTTP_200_OK


class AdmissionApplicantOutSystem(GenericAPIView):
    def put(self, request):
        applicant = ApplicantOutSystemSerializer(data=self.request.data)
        applicant.is_valid(raise_exception=True)
        applicant.update(self.get_applicantID(self.request.data['id']),
                         applicant.validated_data,
                         self.get_user(self.request.session['user']['pk']))
        return Response("Done", status=HTTP_200_OK)

    def get_applicantID(self, id):
        return Applicant.objects.get(id=id)

    def get_user(self, id):
        return User.objects.get(id=id)
