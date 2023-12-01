from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.response import Response
from equations.models.services import Service
from registration.serializers.admin.admissionSerializer import ServiceListSerializer
from registration.models.user_model import User


class ServiceManagement(GenericAPIView):
    serializer_class = ServiceListSerializer
    queryset = Service.objects.all()

    def get(self, request, *args, **kwargs):

        services = ServiceListSerializer(self.get_queryset(), many=True).data
        return Response(services, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        if User.objects.get(id=int(self.request.session['user']['pk'])).role != 6:
            return Response("Unauthorized to Update", status=HTTP_401_UNAUTHORIZED)
        else:
            service_obj = Service.objects.get(name=self.request.data['name'])
            service = ServiceListSerializer(service_obj, data=self.request.data, partial=True)
            service.is_valid(raise_exception=True)
            service.update(service_obj, service.validated_data, int(self.request.session['user']['pk']))
            return Response({"success": "Service Status has been updated.",
                             "success_ar": "تم تعديل الخدمة"}, status=HTTP_200_OK)
