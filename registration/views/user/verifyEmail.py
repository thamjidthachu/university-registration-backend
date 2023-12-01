from django.conf import settings
from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from registration.models.applicant import Applicant


class VerifyEmail(CreateAPIView):
    def post(self, request, *args, **kwargs):
        if 'email' in self.request.data:
            if not self.check_email(self.request.data['email']).exists():
                return Response({"valid": True}, status=HTTP_200_OK)

        return Response({"valid": False}, status=HTTP_200_OK)

    @staticmethod
    def check_email(email):
        return Applicant.objects.filter(email__iexact=email, apply_semester=settings.CURRENT_SEMESTER)
