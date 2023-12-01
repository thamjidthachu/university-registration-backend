from rest_framework.status import HTTP_200_OK
from rest_framework.generics import GenericAPIView
from registration.serializers.admin.admissionSerializer import updatePeriorityApplicantSerializer
from rest_framework.response import Response
from registration.models.applicant import Applicant
from email_handling.views.body_mails import admissionPriorityMail
from registration.tasks import send_email, saved_oracle_process


class AdmissionUpdatePeriority(GenericAPIView):

    def put(self, request, *args, **kwargs):
        applicant = self.get_applicant(self.request.data['id'])
        app = updatePeriorityApplicantSerializer(data=self.request.data)
        app.is_valid(raise_exception=True)
        app.validated_data['user'] = self.request.session['user']['pk']
        applicant = app.update(applicant, app.validated_data)

        saved_oracle_process(applicant.id, applicant.email, applicant.national_id, 5)

        change_reason = self.request.data['change_reason'] if 'change_reason' in self.request.data else ""
        body = admissionPriorityMail(change_reason)
        send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                         applicant.email, english=body['english'], arabic=body['arabic'],
                         subject='Al Maarefa University priorities have been updated',
                         login="Login Now")

        return Response("Done", status=HTTP_200_OK)

    def get_queryset(self, user_id):
        from ....models.user_model import User
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_applicant(self, id):
        return Applicant.objects.get(id=id)
