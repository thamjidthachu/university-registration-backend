from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from registration.serializers.admin.admissionSerializer import addNotesApplicantSerializer, getNotesApplicantSerializer
from rest_framework.response import Response
from registration.models.applicant import Applicant, Note


class AdmissionAddNote(GenericAPIView):
    def get(self, request, *args, **kwargs):
        applicant_id = self.request.query_params.get('id', None)
        if applicant_id:
            app = Note.objects.filter(applicant_name__id=applicant_id)
            if app is None:
                return Response("Applicant Doesn't Exist", status=HTTP_404_NOT_FOUND)
            return Response(getNotesApplicantSerializer(app, many=True).data, status=HTTP_200_OK)
        data = getNotesApplicantSerializer(Note.objects.all(), many=True).data
        return Response(data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        app = addNotesApplicantSerializer(data=self.request.data)
        app.is_valid(raise_exception=True)
        app.validated_data['user'] = int(self.request.session['user']['pk'])
        app.validated_data['applicant'] = self.get_applicant(self.request.data['id'])
        app.create(app.validated_data)
        return Response("Done", status=HTTP_200_OK)

    # def put(self, request, *args, **kwargs):
    #     app = addNotesApplicantSerializer(data=self.request.data)
    #     app.is_valid(raise_exception=True)
    #     app.validated_data['user'] = int(self.request.session['user']['pk'])
    #     app.update(self.get_applicant(self.request.data['id']), app.validated_data)
    #
    #     return Response("Done", status=HTTP_200_OK)

    @staticmethod
    def get_applicant(applicant_id):
        try:
            applicant = Applicant.objects.get(id=applicant_id)
            return applicant
        except Applicant.DoesNotExist:
            return None
