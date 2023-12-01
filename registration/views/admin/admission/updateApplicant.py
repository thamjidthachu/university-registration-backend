from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from registration.serializers.admin.admissionSerializer import AdmissionListApplicant
from registration.models.applicant import Applicant
from registration.tasks import saved_oracle_process


class UpdateApplicant(UpdateAPIView):
    serializer_class = AdmissionListApplicant

    def put(self, request, *args, **kwargs):
        applicant_id = request.query_params.get('id', None)
        if applicant_id:
            applicant = self.get_applicant(applicant_id).last()
            if applicant.id:
                request.data['id'] = applicant.id
                update_applicant = self.serializer_class(applicant, data=request.data)
                update_applicant.is_valid(raise_exception=True)
                update_applicant.update(applicant, update_applicant.validated_data)
                saved_oracle_process.delay(applicant.id, applicant.email, applicant.national_id, 2)
                return Response("successfully updated", status=HTTP_200_OK)

            return Response({"error": "This Applicant isn't found!", "error_ar": "عفوا, لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid passing the parameters"}, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_applicant(applicant_id):
        return Applicant.objects.filter(id=applicant_id)
