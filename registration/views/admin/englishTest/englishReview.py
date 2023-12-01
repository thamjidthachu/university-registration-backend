from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from registration.models.user_model import User
from registration.serializers.admin.englishGradeSerializer import EnglishSerializer, EnglishResultSerializer
from email_handling.views.body_mails import englishPostponedMail, englishAbsentMail, englishFailedMail
from registration.models.evaluation import EnglishTest, Interview, Absent
from registration.models.applicant import Applicant
from registration.tasks import send_email


class EnglishReview(GenericAPIView):

    def put(self, request, *args, **kwargs):
        english = EnglishResultSerializer(data=self.request.data)
        english.is_valid(raise_exception=True)
        english_result = self.get_queryset(self.request.query_params['id'],
                                           self.request.query_params['test_try']).last()
        english.update(english_result,
                       english.validated_data, self.get_user(int(self.request.session['user']['pk'])))
        applicant = english_result.applicant_id
        if "P" == self.request.data['result']:
            body = englishPostponedMail()
            send_email.delay(
                self.request.META.get('HTTP_HOST'), applicant.first_name,
                applicant.email, applicant.arabic_first_name, applicant.gender,
                english=body['english'], arabic=body['arabic'],
                subject='Al Maarefa University KSA English Test Result', link="الدخول لحسابك"
            )

        if "A" == self.request.data['result']:
            body = englishAbsentMail()
            send_email.delay(
                self.request.META.get('HTTP_HOST'), applicant.first_name,
                applicant.email, applicant.arabic_first_name, applicant.gender, english=body['english'],
                arabic=body['arabic'],
                subject='Al Maarefa University KSA English Test Result', link="الدخول لحسابك"
            )

            Absent.objects.create(applicant_id=Applicant.objects.get(id=self.request.query_params['id']),
                                  reservation_id=english_result.reservation_id)
            english_result.reservation_id.count -= 1
            english_result.reservation_id.save()
            english_result.delete()
        if "F" == self.request.data['result']:
            body = englishFailedMail()
            send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                             applicant.email, applicant.arabic_first_name, applicant.gender,
                             english=body['english'], arabic=body['arabic'],
                             subject='Al Maarefa University KSA English Test Result', link="الدخول لحسابك")

        return Response("Done", status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        intr_object = self.get_queryset(self.request.query_params['id'], self.request.query_params['test_try'])
        intr = Interview.objects.filter(applicant_id=self.request.query_params['id'])

        if intr_object.exists():
            english = EnglishSerializer(intr_object.first()).data
            return Response({
                'applicant_id': english.pop('applicant_id'),
                'reservation_id': english.pop('reservation_id'),
                "interview": intr.last().reservation_id.reservation_date if intr.exists() else None,
                'id': english
            }, status=HTTP_200_OK)

        return Response({"Error": "This applicant isn't found!", "error_ar": "هذا الطالب غير موجود"},
                        status=HTTP_404_NOT_FOUND)

    def get_queryset(self, applicant_id, test_try):
        return EnglishTest.objects.filter(applicant_id=applicant_id, test_try=test_try)

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def get_applicant(self, applicant_id):
        return Applicant.objects.get(id=applicant_id)
