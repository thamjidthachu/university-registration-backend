from django.conf import settings
from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from registration.models.applicant import Applicant
from registration.serializers.user.registerSerializer import RegisterSerializer


class VerifyNationalID(CreateAPIView):
    def post(self, request, *args, **kwargs):
        if 'national_id' in self.request.data:
            if not self.check_national_id(self.request.data['national_id']).exists():
                # last_instance = self.last_applicant_instance(self.request.data['national_id'])
                return Response({"valid": True, "record": None}, status=HTTP_200_OK)
                # return Response({"valid": True, "record": RegisterSerializer(last_instance).data if last_instance else None})

        return Response({"valid": False}, status=HTTP_200_OK)

    @staticmethod
    def check_national_id(nid):
        return Applicant.objects.filter(national_id=nid, apply_semester=settings.CURRENT_SEMESTER)

    @staticmethod
    def last_applicant_instance(nid):
        return Applicant.objects.filter(national_id=nid).last()
