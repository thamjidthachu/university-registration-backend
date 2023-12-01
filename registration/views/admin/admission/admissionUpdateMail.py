from rest_framework.status import HTTP_200_OK
from rest_framework.generics import GenericAPIView
from registration.serializers.admin.admissionSerializer import updateMailApplicantSerializer
from registration.serializers.admin.admissionSerializer import ApplicantRetreiveSerializer
from rest_framework.response import Response
from registration.models.applicant import Applicant
from email_handling.views.body_mails import registerMail
from registration.tasks import send_email
from registration.serializers.admin.admissionSerializer import AdmissionListApplicant


class AdmissionUpdateMail(GenericAPIView):

    def get(self, request, *args, **kwargs):
        applicant = self.get_applicant(self.request.query_params['id'])
        profile = ApplicantRetreiveSerializer(applicant).data

        return Response({"profile": profile,
                         "register_data": AdmissionListApplicant(applicant).data
                         }, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):

        app = updateMailApplicantSerializer(data=self.request.data)
        app.is_valid(raise_exception=True)
        app.validated_data['user'] = self.request.session['user']['pk']
        app.update(self.get_applicant(self.request.data['id']), app.validated_data)

        applicant = self.get_applicant(self.request.data['id'])
        body = registerMail()
        send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                         applicant.email, applicant.arabic_first_name, applicant.gender, english=body['english'],
                         arabic=body['arabic'],
                         subject='Al Maarefa University Registration succeeded',
                         login="Login Now"
                         )
        return Response("Done", status=HTTP_200_OK)

    def get_queryset(self, user_id):
        from ....models.user_model import User
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_applicant(self, id):
        return Applicant.objects.get(id=id)
