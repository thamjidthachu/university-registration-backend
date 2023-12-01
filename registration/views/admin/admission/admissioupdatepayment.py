import logging
import secrets
import string

from django.conf import settings
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from registration.models.applicant import Payment, Applicant, User
from registration.models.evaluation import EnglishTest
from registration.models.sysadmin import UnivPayments
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.user.paymentSerializer import PaySerializer, PayGetSerializer

logger = logging.getLogger("payment_logs")


class PaymentByCash(GenericAPIView):
    pagination_class = ApplicantListPagination()

    def get(self, *args, **kwargs):
        try:
            applicant_id = self.request.query_params.get('applicant_id', None)
            if applicant_id:
                payment = Payment.objects.filter(applicant_id_id=applicant_id, by_cash=True)
                data = PayGetSerializer(payment, many=True).data
                return Response(data, status=HTTP_200_OK)

            major = self.request.query_params.get('major', None)
            semester = self.request.query_params.get('semester', None)
            paid = self.request.query_params.get('paid', None)

            payment_type = kwargs.get('type', 'all')
            payment_object_filters = self.get_payment_object_filters_data(
                paid=paid,
                payment_type=payment_type,
                major=major,
                semester=semester
            )

            query = self.request.query_params.get('query')
            if query not in ["", None]:
                payment_object_filters = payment_object_filters.filter(
                    Q(applicant_id__national_id__istartswith=query) | Q(applicant_id__last_name__icontains=query)
                    | Q(applicant_id__arabic_full_name__istartswith=query) | Q(applicant_id__email__istartswith=query)
                    | Q(applicant_id__full_name__istartswith=query) | Q(applicant_id__arabic_last_name__icontains=query)
                )

            if not payment_object_filters.exists():
                return Response(
                    {"warning": "No Payments data found.", "warning_ar": "لم يتم العثور على بيانات المدفوعات."},
                    status=400
                )

            payment_object_filters_pagination = self.pagination_class.paginate_queryset(
                payment_object_filters,
                self.request
            )

            return self.pagination_class.get_paginated_response(
                PayGetSerializer(payment_object_filters_pagination, many=True).data
            )

        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        if kwargs['type'] in ['retest', 'register', 'equation']:
            try:
                applicant = Applicant.objects.filter(
                    id=self.request.data['applicant_id'],
                    apply_semester=settings.CURRENT_SEMESTER).last()
                if not applicant:
                    return Response(
                        {"warning": "Sorry, you can\'t pay at the current semester.",
                         "warning_ar": "عفواً، لا يمكنك الدفع في هذا الفصل."}, status=HTTP_404_NOT_FOUND)

                cost = None
                payment_type = kwargs['type']
                if payment_type == 'retest':
                    if Payment.objects.filter(
                            by_cash=True, applicant_id=self.request.data['applicant_id'], paid=False,
                            payment_id__payment_title='ERET').exists():
                        return Response(
                            {"warning": "Already a cash payment exists. Pls pay that first",
                             "warning_ar": "يوجد بالفعل دفع نقدي. الثابتة والمتنقلة دفع ذلك أولا"},
                            status=HTTP_404_NOT_FOUND)

                    if Payment.objects.filter(by_cash=True, applicant_id=self.request.data['applicant_id'],
                                              payment_id__payment_title='ERET').count() >= 3:
                        return Response(
                            {"warning": "You have already exhausted maximum try of 3 english tests.",
                             "warning_ar": "لقد استنفدت بالفعل الحد الأقصى من 3 اختبارات للغة الإنجليزية."},
                            status=HTTP_404_NOT_FOUND)

                    cost = self.get_amount("ERET")

                elif payment_type == 'register':
                    equation_payment = Payment.objects.filter(applicant_id=self.request.data['applicant_id'],
                                                              payment_id__payment_title='EQU').last()
                    if equation_payment and equation_payment.paid:
                        cost = self.get_amount("REG") - self.get_amount("EQU")
                    else:
                        cost = self.get_amount("REG")

                elif payment_type == 'equation':
                    registration_payment = Payment.objects.filter(applicant_id=self.request.data['applicant_id'],
                                                                  payment_id__payment_title='REG').last()
                    if registration_payment and registration_payment.paid:
                        return Response("You already paid the fees", status=HTTP_200_OK)
                    cost = self.get_amount("EQU")

                if cost is None:
                    return Response(
                        {"warning": "Not Opened yet!", "warning_ar": "لم يتم فتحه بعد"},
                        status=HTTP_404_NOT_FOUND)

                if int(applicant.national_id[0]) != 1:
                    cost = "%0.2f" % float(float(cost) + (float(cost) * float(15 / 100)))

                payment_type = self.get_payment_type_name_filter(kwargs['type'])
                unique_mix = self.generate_unique_code(20)
                checkout_id_with_unique_mix = f"cash_{unique_mix}"

                checkout = PaySerializer(data={
                    "checkout_id": checkout_id_with_unique_mix,
                    "amount": cost,
                    "entity_id": "None",
                    "applicant_id": self.request.data['applicant_id'],
                    'type': payment_type,
                    "by_cash": True
                })
                checkout.is_valid(raise_exception=True)
                checkout.create(checkout.validated_data, payment_type)
                return Response(data=checkout.data, status=HTTP_200_OK)

            except Exception as e:
                return Response({"error": "Something went wrong", "details": str(e)},
                                status=HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "Request Not Found", "error_ar": "الطلب غير موجود"}, status=HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        if kwargs['type'] == 'confirm':
            try:
                english_test = None
                applicant_id = self.request.data.get('applicant_id')
                checkout_id = self.request.data.get('checkout_id')
                payment_confirmer = self.get_user(int(self.request.session['user']['pk']))

                if not payment_confirmer:
                    return Response({"warning": "Sorry, Invalid credentials.",
                                     "warning_ar": "عذرا ، بيانات الاعتماد غير صالحة."}, status=HTTP_404_NOT_FOUND)

                payment_object = Payment.objects.filter(applicant_id=applicant_id, checkout_id=checkout_id,
                                                        by_cash=True,
                                                        paid=False)

                if not payment_object:
                    return Response({"warning": "Sorry, Payment details not found .",
                                     "warning_ar": "عذرا ، تفاصيل الدفع غير موجودة."}, status=HTTP_404_NOT_FOUND)

                if payment_object[0].payment_id.payment_title == 'ERET':
                    english_test = EnglishTest.objects.filter(applicant_id_id=applicant_id, paid=False).last()
                    if not english_test:
                        return Response(
                            {"warning": "Sorry, No English Test has found for this Applicant.",
                             "warning_ar": ".عذرا ، لم يتم العثور على اختبار اللغة الإنجليزية لمقدم الطلب هذا."},
                            status=HTTP_404_NOT_FOUND)
                    else:
                        english_test.paid = True
                        english_test.save()

                payment_object.update(paid=True, payment_confirmer=payment_confirmer,
                                      clearing_institute_name='al-maarefa')

                return Response({"success": "Paid Successfully.", "success_ar": "تم الدفع بنجاح"}, status=HTTP_200_OK)

            except Exception as e:
                return Response({"error": "Something went wrong", "details": str(e)},
                                status=HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"error": "Request Not Found", "error_ar": "الطلب غير موجود"}, status=HTTP_404_NOT_FOUND)

    def get_payment_object_filters_data(self, paid, payment_type, major, semester):
        query = Payment.objects.filter(by_cash=True, applicant_id__apply_semester=semester)

        if paid not in ['all', None, '']:
            query = query.filter(paid=paid)

        if major not in ['all', None, '']:
            query = query.filter(applicant_id__major_id__name=major)

        if payment_type not in ['all', None, '']:
            title = self.get_payment_type_name_filter(payment_type)
            query = query.filter(payment_id__payment_title=title)

        return query.order_by('-id')

    @staticmethod
    def get_payment_type_name_filter(title):
        result = {
            "retest": "ERET",
            "register": "REG",
            "equation": "EQU"
        }

        if title in result:
            return result[title]

        return -1

    @staticmethod
    def get_amount(title):
        cost = UnivPayments.objects.filter(payment_title=title)
        if cost.exists():
            return cost.last().cost
        return None

    @staticmethod
    def generate_unique_code(length):
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def get_user(pk):
        return User.objects.get(id=pk)
