from rest_framework.status import HTTP_200_OK
from rest_framework.generics import GenericAPIView
from registration.serializers.admin.admissionSerializer import UpdateScoreApplicantSerializer
from rest_framework.response import Response
from registration.models.applicant import Applicant
from registration.tasks import saved_oracle_process


class AdmissionUpdateScore(GenericAPIView):

    def put(self, request, *args, **kwargs):
        applicant = self.get_applicant(self.request.data['id'])
        app = UpdateScoreApplicantSerializer(data=self.request.data)
        app.is_valid(raise_exception=True)
        app.validated_data['user'] = self.request.session['user']['pk']
        app = app.update(applicant, app.validated_data)
        saved_oracle_process.delay(app.id, app.email, app.national_id, 3)

        return Response("Done", status=HTTP_200_OK)


    def get_applicant(self, id):
        return Applicant.objects.get(id=id)

