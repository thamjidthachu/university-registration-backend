from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.generics import GenericAPIView
from registration.models.applicant import Applicant
from sms.smsSend import SmsSend


class AutomatedSendSmsWaitingPay(GenericAPIView):

    def post(self, request, *args, **kwargs):
        applicants, last_id = self.get_queryset(self.request.data['last_id'])

        if applicants is not None:
            message = "جامعة المعرفة تهنئك على القبول وتطلب منك المبادرة بسداد رسوم التسجيل عبر منصة القبول ليتم إصدار الرقم الجامعي"
            for app in applicants:
                if app.phone is not None:
                    SmsSend().sendSingleNumber(app.phone, message)
                    fn = open("log_sms_waiting_pay", "a+")
                    fn.write(
                        str(app.full_name) + " ----- has been Sent\n<------------------------------------------------------------------------>\n")
                    fn.close()
            return Response({
                "last_id": applicants[len(applicants) - 1].id,
                "total": last_id
            }, status=HTTP_200_OK)

        else:
            return Response("empty", status=HTTP_200_OK)


    def get_queryset(self, id):

        applicants = Applicant.objects.raw("select id, phone from registration_applicant where offer='AC' and accepted_outside = false and id > %s and id not in (select applicant_id_id from registration_payment p join registration_univpayments u on p.payment_id_id = u.id where u.payment_title='REG') order by registration_date;", [id])
        if len(applicants) > 0:
            return applicants[:5], applicants[len(applicants) - 1].id

        return None, 0
