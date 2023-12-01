import json
import logging
import re
import urllib

from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from email_handling.views.body_mails import paymentMail
from registration.tasks import send_email, save_payment_oracle_process
from ...models.applicant import Payment, Applicant
from ...models.evaluation import EnglishTest
from ...models.sysadmin import UnivPayments
from ...serializers.user.paymentSerializer import PaySerializer, PayUpdateSerializer

logger = logging.getLogger("payment_logs")


class ApplicantPay(GenericAPIView):

    def post(self, request, *args, **kwargs):
        if kwargs['type'] in ['retest', 'register', 'equation']:

            applicant = Applicant.objects.filter(id=self.request.data['applicant_id'],
                                                 apply_semester=settings.CURRENT_SEMESTER).last()

            if not applicant:
                return Response({"warning": "Sorry, you can\'t pay at the current semester.",
                                 "warning_ar": "عفواً، لا يمكنك الدفع في هذا الفصل."}, status=HTTP_404_NOT_FOUND)

            cost = None
            payment_type = kwargs['type']
            if payment_type == 'retest':
                Payment.objects.filter(by_cash=True,applicant_id=self.request.data['applicant_id'],paid=False,payment_id__payment_title='ERET').delete()
                cost = self.get_amount("ERET")

            elif payment_type == 'register':
                equation_payment = Payment.objects.filter(applicant_id=self.request.data['applicant_id'],
                                                          payment_id__payment_title='EQU').last()

                if equation_payment:
                    if equation_payment.paid:
                        cost = self.get_amount("REG") - self.get_amount("EQU")
                    else:
                        cost = self.get_amount("REG")
                else:
                    cost = self.get_amount("REG")

            elif payment_type == 'equation':
                registration_payment = Payment.objects.filter(applicant_id=self.request.data['applicant_id'],
                                                              payment_id__payment_title='REG').last()
                if registration_payment:
                    if registration_payment.paid:
                        return Response("You already paid the fees", status=HTTP_200_OK)
                    else:
                        cost = self.get_amount("EQU")
                else:
                    cost = self.get_amount("EQU")

            applicant_national_id = applicant.national_id

            if cost is None:
                return Response({"warning": "Not Opened yet!", "warning_ar": "لم يتم فتحه بعد"}, status=HTTP_404_NOT_FOUND)

            if int(applicant_national_id[0]) != 1:
                cost = "%0.2f" % float(float(cost) + (float(cost) * float(15 / 100)))

            url = settings.PAYMENT_BASE_URL + "/v1/checkouts"

            if self.request.data['brand'] == "VISA":
                entityId = settings.VISA_ENTITY_ID
            else:
                entityId = settings.MADA_ENTITY_ID

            data = {
                'amount': int(float(cost)),
                'currency': 'SAR',
                'paymentType': 'DB',
                "entityId": entityId
            }
            logger.debug(f"[TYPE] of cost is {type(cost)}")

            try:
                logger.debug(
                    f"[PAYMENT-CHECKOUT-REQUEST-DATA] applicant {applicant_national_id} and request data {self.request.data} - {kwargs} and payment data are {data}")

                request = urllib.request.Request(url, urllib.parse.urlencode(data).encode('ascii'))
                request.add_header('Authorization', f'Bearer {settings.PAYMENT_SECRET_KEY}')
                request.get_method = lambda: 'POST'
                response = urllib.request.urlopen(request)
                logger.debug(f"[RESPONSE-FROM-HYPERPAY] - {response}")
                data = json.loads(response.read().decode("utf-8"))

                logger.debug(
                    f"[PAYMENT-CHECKOUT-RESPONSE-DATA] applicant {applicant_national_id} and request data {self.request.data} - {kwargs} and payment response data {data}")

                payment_type = ''
                if kwargs['type'] == 'equation':
                    payment_type = 'EQU'
                if kwargs['type'] == 'retest':
                    payment_type = 'ERET'
                if kwargs['type'] == 'register':
                    payment_type = 'REG'

                checkout = PaySerializer(data={
                    "checkout_id": data['id'],
                    "entity_id": entityId,
                    "applicant_id": self.request.data['applicant_id'],
                    'type': payment_type
                })
                checkout.is_valid(raise_exception=True)
                if 'app' not in checkout.validated_data:
                    checkout.create(checkout.validated_data, payment_type)
                else:
                    checkout.update(checkout.validated_data['app'], checkout.validated_data)

                return Response(data, status=HTTP_200_OK)

            except (urllib.error.URLError, Exception) as e:

                data = json.loads(e.read())
                logger.debug(
                    f"[PAYMENT-CHECKOUT-REQUEST-FAIL] applicant {applicant_national_id} and request data {self.request.data} - {kwargs} and error {data}")
                return Response(data)
        else:

            return Response({"error": "Request Not Found", "error_ar": "الطلب غير موجود"}, status=HTTP_404_NOT_FOUND)

    def get(self, *args, **kwargs):

        if kwargs['type'] == 'status':
            checkoutId = None
            if 'process_id' in self.request.query_params:
                checkoutId = self.request.query_params['process_id']
            else:
                return Response({"result": {"description": "Error not found", "description_ar": "غير موجود"}},
                                status=HTTP_404_NOT_FOUND)

            payment = Payment.objects.get(checkout_id=self.request.query_params['process_id'])

            url = f"{settings.PAYMENT_BASE_URL}/v1/checkouts/{checkoutId}/payment?entityId={payment.entity_id}"

            try:
                request = urllib.request.Request(url)
                request.add_header('Authorization', f'Bearer {settings.PAYMENT_SECRET_KEY}')
                request.get_method = lambda: 'GET'
                response = urllib.request.urlopen(request)
                resp = response.read().decode("utf-8")
                resp = json.loads(resp)

                logger.debug(
                    f"[PAYMENT-TRX-RESPONSE] applicant {payment.applicant_id.national_id} and request data {self.request.query_params} - {kwargs} response data {resp}")

                if re.match(r'^(000\.000\.|000\.100\.1|000\.[36])', resp['result']['code']) \
                        or re.match(r'^(000\.400\.0[^3]|000\.400\.100)', resp['result']['code']):

                    auth = resp.get('resultDetails', {}).get('AuthorizationCode', None) or resp.get('resultDetails',
                                                                                                    {}).get('AuthCode',
                                                                                                            None)

                    paid_data = {
                        "paid": True,
                        "transaction_id": resp.get('id'),
                        "amount": resp.get('amount'),
                        "card_number": resp.get('card', {}).get('bin', "") + "*******" + resp.get('card', {}).get(
                            'last4Digits', ""),
                        "authorization_code": auth,
                        "clearing_institute_name": resp.get('resultDetails', {}).get('clearingInstituteName', ""),
                        "ipCountry": resp.get('customer', {}).get('ipCountry', ""),
                        "ipAddr": resp.get('customer', {}).get('ip', ""),
                    }
                    logger.debug(
                        f"[PAYMENT-TRX-PAID-DATA] applicant {payment.applicant_id.national_id} and request data {self.request.query_params} - {kwargs} with paid data {paid_data}")
                    paid = PayUpdateSerializer(payment, data=paid_data)

                    paid.is_valid(raise_exception=True)
                    paid.update(payment, paid.validated_data)
                    # to update status of english payment after successfully payment for english retest
                    if payment.payment_id.payment_title == 'ERET':
                        EnglishTest.objects.filter(applicant_id=payment.applicant_id, paid=False).update(paid=True)
                    try:
                        logger.debug(
                            f"[values] - {payment.applicant_id} -> {type(payment.applicant_id)} | {payment} --> {type(payment)}")
                        logger.debug(f"[DICT] - {payment.payment_id.payment_title}")
                        save_payment_oracle_process(
                            payment.applicant_id,
                            payment,
                            payment.payment_id.payment_title
                        )
                    except Exception as e:
                        logger.debug(
                            f"[SAVE-PAYMENT-EXCEPTION] - {e}")

                    body = paymentMail(payment)
                    send_email.delay(request.headers.get("origin"), payment.applicant_id.first_name,
                                     payment.applicant_id.email, english=body['english'], arabic=body['arabic'],
                                     subject='l Maarefa University Successful payment', link="Go to Dashboard")

                    return Response(resp, status=response.code)

                elif re.match(r'^(000\.200)', resp['result']['code']):
                    return Response(resp, status=HTTP_200_OK)

                else:

                    return Response(resp, status=HTTP_400_BAD_REQUEST)

            except (urllib.error.URLError, Exception) as e:
                data = json.loads(e.read())
                logger.debug(
                    f"[PAYMENT-TRX-FAIL] applicant {payment.applicant_id.national_id}  and request data {self.request.query_params} - {kwargs} with error {data}")
                return Response(data, status=e.code)

        else:
            return Response({"error": "Request Not Found", "error_ar": "الطلب غير موجود"}, status=HTTP_404_NOT_FOUND)

    @staticmethod
    def get_amount(title):
        cost = UnivPayments.objects.filter(payment_title=title)
        if cost.exists():
            return cost.last().cost
        return None
