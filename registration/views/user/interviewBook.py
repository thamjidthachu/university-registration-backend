from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from registration.serializers.user.interviewBookSerializer import InterviewBookSerializer
from email_handling.views.body_mails import interviewBookMail_online, interviewBookMail_offline
from django.utils.timezone import datetime
from sms.smsSend import SmsSend
from registration.models.applicant import Reservation, Applicant
from registration.tasks import send_email


# Implemented By Mohamed Samy.

class InterviewBook(GenericAPIView):
    serializer_class = InterviewBookSerializer

    def post(self, request, *args, **kwargs):

        # self.request.data['applicant_id'] = int(self.request.session['user']['pk'])
        reserve = InterviewBookSerializer(data=self.request.data)

        if reserve.is_valid():
            reserve.create(reserve.validated_data)
            reserve.update(reserve.validated_data['reservation_id'])
            applicant = reserve.validated_data.get("applicant_id")
            reservation = reserve.validated_data.get('reservation_id')
            if reservation.online:
                body = interviewBookMail_online(reservation)
                send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                                 applicant.email, applicant.arabic_first_name, applicant.gender,
                                 english=body['english'], arabic=body['arabic'],
                                 subject='Al Maarefa University Interview confirmation', link="Go to Dashboard",
                                 file='interview')

            else:
                body = interviewBookMail_offline(reservation)
                send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                                 applicant.email, applicant.arabic_first_name, applicant.gender,
                                 english=body['english'], arabic=body['arabic'],
                                 subject='Al Maarefa University Interview confirmation', link="Go to Dashboard")

            message = "جامعة المعرفة تشعرك بأن موعد المقابلة في يوم " + str(
                reservation.reservation_date) + " الساعة " + str(
                reservation.start_time) + " تابع ايميلك للحصول على تفاصيل المقابلة."
            try:
                SmsSend().sendSingleNumber(applicant.phone, message)
            except Exception as e:
                pass
            full_capacity = False
            reservations = Reservation.objects.get(id=self.request.data['reservation_id'])
            if reservations.count == reservations.capacity:
                full_capacity = True
            return Response({"full_capacity": full_capacity}, status=HTTP_200_OK)
        else:
            return Response(reserve.errors, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self, id=None, test_type=None, capacity=None):
        try:
            if id is not None:
                return Reservation.objects.get(id=id, test_type=test_type)
            else:
                return Reservation.objects.filter(test_type=test_type,
                                                  capacity__gt=capacity,
                                                  resveration_date__gt=datetime.now().date())
        except Reservation.DoesNotExist:
            return None

    def delete(self, instance):
        reservations = Reservation.objects.get(id=self.request.data['reservation_id'])
        reservations.reserved = False
        reservations.save()
        return Response({"status": "Cancelled Reservation!!"}, status=HTTP_200_OK)

    def get_applicant(self, id):
        return Applicant.objects.get(id=id)
