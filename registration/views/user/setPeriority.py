from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from ...serializers.user.uploadSerializer import PerioritySerializer
from ...models.applicant import Applicant
from registration.tasks import saved_oracle_process

# Implemented By Hassan Mokhtar.


class Periority(GenericAPIView):

    serializer_class = PerioritySerializer

    def put(self, request):
        app = Applicant.objects.get(id=int(self.request.session['user']['pk']))
        major_set = PerioritySerializer(data=self.request.data)
        major_set.is_valid(raise_exception=True)
        app = major_set.update(app, major_set.validated_data)

        saved_oracle_process.delay(app.id, app.email, app.national_id, 4)

        return Response("priorities added", status=HTTP_200_OK)

    def get_queryset(self, id):
        return Applicant.objects.get(id=id)
