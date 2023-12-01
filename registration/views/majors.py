from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from registration.models.univStructure import Major
from registration.serializers.admin.admissionSerializer import MajorListSerializer


class AllMajorsView(ListAPIView):

    def get(self, request, *args, **kwargs):
        majors = Major.objects.all()
        majors_data = MajorListSerializer(majors, many=True).data
        return Response({
            'majors': majors_data
        }, status=HTTP_200_OK)
