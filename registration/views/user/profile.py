from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.generics import GenericAPIView
from ...models.applicant import Applicant
from ...serializers.user.applicantProfile import ApplicantProfileUpdateSerializer


class Profile(GenericAPIView):

    def put(self, request, *args, **kwargs):
        applicant = ApplicantProfileUpdateSerializer(data=self.request.data)
        applicant.is_valid(raise_exception=True)
        applicant.update(Applicant.objects.get(id=applicant.validated_data['id']), applicant.validated_data)
        return Response("Done", status=HTTP_200_OK)
