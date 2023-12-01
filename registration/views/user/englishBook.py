from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from ...serializers.user.bookDateSerializer import SetBookEnglishSerializer
from email_handling.views.body_mails import englishBookMail_online, englishBookMail_offline
from sms.smsSend import SmsSend
from registration.models.applicant import Reservation, Applicant
from registration.tasks import send_email


class EnglishBook(GenericAPIView):

    def post(self, request):
        reservation = SetBookEnglishSerializer(data=self.request.data)
        reservation.is_valid(raise_exception=True)
        reservation.create(reservation.validated_data)
        applicant = reservation.validated_data['applicant_id']
        reserv = reservation.validated_data['reservation_id']
        if reserv.online:
            body = englishBookMail_online(reserv)
            send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                             applicant.email, applicant.arabic_first_name, applicant.gender, english=body['english'],
                             arabic=body['arabic'],
                             subject='Al Maarefa University English confirmation', link="Go to Dashboard",
                             file='english')
        else:
            body = englishBookMail_offline(reserv)
            send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                             applicant.email, applicant.arabic_first_name, applicant.gender, english=body['english'],
                             arabic=body['arabic'],
                             subject='Al Maarefa University English confirmation', link="Go to Dashboard")

        message = "جامعة المعرفة تشعرك بأن اختبار اللغة في يوم " + str(reserv.reservation_date) + " الساعة " + str(
            reserv.start_time) + " تابع ايميلك للحصول على تفاصيل الاختبار"
        try:
            SmsSend().sendSingleNumber(applicant.phone, message)
        except Exception as e:
            pass
        full_capacity = False
        reservations = Reservation.objects.get(id=self.request.data['reservation_id'])
        if reservations.count == reservations.capacity:
            full_capacity = True
        return Response({"full_capacity": full_capacity}, status=HTTP_200_OK)

    def delete(self, instance):
        reservations = Reservation.objects.get(id=self.request.data['reservation_id'])
        reservations.reserved = False
        reservations.save()
        return Response({"status": "Cancelled Reservation!!"}, status=HTTP_200_OK)

    @staticmethod
    def get_applicant(applicant_id):
        return Applicant.objects.get(id=applicant_id)
