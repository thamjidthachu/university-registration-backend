from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from ....models.applicant import Applicant
from registration.tasks import send_email


class SendCustomEmail(CreateAPIView):

    def post(self, request, *args, **kwargs):
        applicant = self.get_applicant(self.request.data['id'])
        send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                         applicant.email, english=tuple(self.request.data['body'].split('\n')),
                         arabic=None,
                         subject='Al Maarefa University additional information')

        return Response({"Success": "Successfully sent"}, status=HTTP_200_OK)

    def get_applicant(self, id):
        return Applicant.objects.get(id=id)
