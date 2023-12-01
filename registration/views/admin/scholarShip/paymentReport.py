from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from registration.models.applicant import Payment, Applicant, UnivPayments, GENDER_CHOICES
from rest_framework.generics import GenericAPIView
from registration.serializers.admin.scholarSerializer import PaymentListSerializer
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.admissionSerializer import ApplicantRetreiveSerializer
from django.db.models import Q
from cache.cacheSerializer import CacheSerializer
from cache.cacheModel import CacheModel
from registration.signals.payment import Signal


class PaymentReport(GenericAPIView):
    pagination_class = ApplicantListPagination()

    def get(self, request, *args, **kwargs):
        if 'id' in self.request.query_params:
            try:
                id = int(self.request.query_params['id'])
            except Exception as e:
                return Response({"warning": "Invalid passing the parameters",
                                 "warning_ar": "خطأ في إرسال البيانات"},
                                status=HTTP_400_BAD_REQUEST)

            applicant = Applicant.objects.filter(id=id)
            if applicant.exists():
                return Response(ApplicantRetreiveSerializer(applicant.last()).data, status=HTTP_200_OK)

            return Response({"warning": "Applicant does not exist", "warning_ar": "هذا الطالب غير موجود"},
                            status=HTTP_404_NOT_FOUND)

        cache_name_model = "payment_" + self.request.query_params['semester'] + "_" + \
                           ((self.request.query_params[
                                 'gender'] + "_") if 'gender' in self.request.query_params else "") + \
                           ((self.request.query_params[
                                 'fees'] + "_") if 'fees' in self.request.query_params else "") + "_model"
        cache_name_serializer = "payment_" + self.request.query_params['semester'] + "_" + \
                                ((self.request.query_params[
                                      'gender'] + "_") if 'gender' in self.request.query_params else "") + \
                                ((self.request.query_params[
                                      'fees'] + "_") if 'fees' in self.request.query_params else "") + "_serializer"

        pay_lst = self.get_applicants(self.get_queryset, cache_name_model, self.request.query_params)

        query = self.request.query_params.get('query')
        if query not in ["", None]:
            pay_lst = pay_lst.filter(Q(applicant_id__national_id__istartswith=query) |
                                     Q(applicant_id__arabic_full_name__istartswith=query) |
                                     Q(applicant_id__full_name__istartswith=query) |
                                     Q(applicant_id__email__istartswith=query) |
                                     Q(applicant_id__arabic_last_name__icontains=query) |
                                     Q(applicant_id__last_name__icontains=query)
                                     ).order_by("-payment_date")

        if pay_lst is None or not pay_lst.exists():
            return Response({"warning": "Applicants does not exists", "warning_ar": "لا يوجد طلاب"},
                            status=HTTP_404_NOT_FOUND)

        applicant_data_pagination = self.pagination_class.paginate_queryset(
            pay_lst,
            self.request
        )

        applicants = self.get_data(serializer_class=PaymentListSerializer,
                                   data=applicant_data_pagination,
                                   cache_name=cache_name_serializer)

        applicants, total = self.prepare_total_vat(applicants)

        return Response({
            "count": self.pagination_class.page.paginator.count,
            "next": self.pagination_class.get_next_link(),
            "previous": self.pagination_class.get_previous_link(),
            "results": applicants,
            "total_In_come": total,
        }, status=HTTP_200_OK)

    def get_queryset(self, params):

        if 'semester' not in params:
            return

        kwargs = {}
        kwargs['applicant_id__apply_semester'] = params['semester']

        if 'fees' in params:
            if params['fees'] in dict(UnivPayments.PAY_TYPE).keys():
                kwargs['payment_id__payment_title__exact'] = params['fees']

        if 'from' in params and 'to' in params:
            if params['from'] != "":
                kwargs['payment_date__date__gte'] = params['from']
            if params['to'] != "":
                kwargs['payment_date__date__lte'] = params['to']

        if 'gender' in params:
            if params['gender'] in dict(GENDER_CHOICES).keys():
                kwargs['applicant_id__gender__exact'] = params['gender']

        return Payment.objects.filter(paid=True, **kwargs).order_by("-payment_date")

    def get_applicants(self, function, cache_name, *args, **kwargs):
        if Signal.SIGNAL_PAYMENT:
            CacheModel.remove_cache(CacheModel.list_filter("payment_"))
            Signal.SIGNAL_PAYMENT = False

        return CacheModel(function=function, cache_name=cache_name, params=args, kwargs=kwargs).get_from_cache()

    def get_data(self, serializer_class, data, cache_name, many=True):
        return CacheSerializer(serializer=serializer_class, data=data, cache_name=cache_name,
                               many=many).get_from_cache()

    def prepare_total_vat(self, pay_lst):
        total = 0
        for app in pay_lst:

            if app['applicant_id']['national_id'].startswith("1"):
                app['payment_id']['cost'] = float(app['amount']).__round__(2)
                app['total'] = float(app['amount']).__round__(2)
                app['VAT'] = None

            else:
                app['payment_id']['cost'] = float(
                    float(app['amount']) - ((float(app['amount'] * 0.15)) / (1 + 0.15))).__round__(2)
                app['total'] = app['amount']
                app['VAT'] = float(app['amount'] - app['payment_id']['cost'])

            if app['amount'] is not None:
                total += float(app['amount']).__round__(2)

        return pay_lst, total
