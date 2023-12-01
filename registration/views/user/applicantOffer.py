from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.generics import GenericAPIView
from ...serializers.user.applicantOfferSerializer import ApplicantOfferSerializer
from ...models.applicant import Applicant


class ApplicantOffer(GenericAPIView):
    def put(self, request):
        applicant = ApplicantOfferSerializer(data=self.request.data)
        if applicant.is_valid():
            applicant.update(self.get_queryset(int(self.request.session['user']['pk'])), applicant.validated_data)
            return Response("done", status=HTTP_200_OK)
        else:
            return Response(applicant.errors, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self, id):
        return Applicant.objects.get(id=id)