from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from registration.serializers.admin.admissionSerializer import SetDateSerializer, AdmissionSetInterviewSerializer, AdmissionUpdateApplicantSerializer
from registration.models.evaluation import Interview


class AdmissionInterviewGrade(CreateAPIView):

    def post(self, request, *args, **kwargs):
        if "start_time" in self.request.data and 'test_date' in self.request.data and 'date_type' in self.request.data:
            applicant = self.get_applicant_interview(self.request.data['applicant_id'])
            if applicant.exists():
                applicant = applicant.last()
                if applicant.result is not None or applicant.user is not None:
                    return Response({"error": "This applicant already reviewed from " + str(applicant.user.full_name)},
                                    status=HTTP_400_BAD_REQUEST)

                self.request.data['user'] = int(self.request.session['user']['pk'])
                intr = AdmissionUpdateApplicantSerializer(data=self.request.data)
                intr.is_valid(raise_exception=True)
                intr.update(applicant, intr.validated_data)

            else:

                date_data = {
                    "start_time": self.request.data['start_time'],
                    "reservation_date": self.request.data['test_date'],
                    "test_type": self.request.data['date_type'],
                    "capacity": 1,
                    "duration_time": 1,
                    "user": int(self.request.session['user']['pk'])

                }
                date = SetDateSerializer(data=date_data)
                date.is_valid(raise_exception=True)
                date = date.save()
                self.request.data['reservation_id'] = date.id
                self.request.data['user'] = int(self.request.session['user']['pk'])
                reservation = AdmissionSetInterviewSerializer(data=self.request.data)
                reservation.is_valid(raise_exception=True)
                reservation.create(reservation.validated_data)

            return Response({"success": "Successfully added"}, status=HTTP_200_OK)

        return Response({"error": "Invalid passing parameter"}, status=HTTP_400_BAD_REQUEST)

    def get_applicant_interview(self, id):
        return Interview.objects.filter(applicant_id_id=id)
