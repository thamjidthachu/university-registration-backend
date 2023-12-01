from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from registration.models.sysadmin import UnivPayments
from rest_framework.generics import GenericAPIView
from registration.serializers.admin.scholarSerializer import ScholarFeesListSerializer, ScholarFeesSetSerializer, \
    ScholarFeesUpdateSerializer


class ScholarShipFees(GenericAPIView):
    queryset = UnivPayments.objects.all()

    def get(self, request, *args, **kwargs):
        return Response(ScholarFeesListSerializer(self.get_queryset(), many=True).data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        payment = ScholarFeesSetSerializer(data=self.request.data)
        payment.is_valid(raise_exception=True)
        payment.validated_data['user'] = self.request.session['user']['pk']
        payment.create(payment.validated_data)
        return Response(ScholarFeesListSerializer(self.get_queryset(), many=True).data, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        payment = ScholarFeesUpdateSerializer(data=self.request.data)
        payment.is_valid(raise_exception=True)
        payment.update(UnivPayments.objects.get(payment_title=self.request.data['payment_title']),
                       payment.validated_data
                       )
        return Response(ScholarFeesListSerializer(self.get_queryset(), many=True).data, status=HTTP_200_OK)
