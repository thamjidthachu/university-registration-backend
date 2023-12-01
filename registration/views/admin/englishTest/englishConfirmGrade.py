from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from registration.serializers.admin.englishGradeSerializer import EnglishSerializer, EnglishConfirmSerializer
from email_handling.views.body_mails import englishTestMail
from registration.models.evaluation import EnglishTest
from registration.tasks import send_email


class EnglishConfirmGrade(GenericAPIView):

    def put(self, request, *args, **kwargs):
        english = EnglishConfirmSerializer(data=self.request.data)
        english.is_valid(raise_exception=True)
        english_result = self.get_english_test(self.request.query_params.get('id'), self.request.query_params.get('try'))
        english.update(english_result, english.validated_data)

        if english.validated_data['confirmed']:
            body = englishTestMail(english_result)
            send_email.delay(
                self.request.META.get('HTTP_HOST'), english_result.applicant_id.first_name,
                english_result.applicant_id.email, english_result.applicant_id.arabic_first_name,
                english_result.applicant_id.gender, english=body['english'], arabic=body['arabic'],
                subject='Al Maarefa University English Test Result', link="الدخول لحسابك"
            )

        return Response("Done", status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        applicant = self.get_english_test(self.request.query_params.get('id'), self.request.query_params.get('try'))
        english = EnglishSerializer(applicant).data
        return Response({
            'applicant_id': english.pop('applicant_id'),
            'reservation_id': english.pop('reservation_id'),
            'user_staff': english.pop('user'),
            'id': english,
        }, status=HTTP_200_OK)

    @staticmethod
    def get_english_test(applicant_id, tries):
        if applicant_id is not None and tries is not None:
            return EnglishTest.objects.filter(applicant_id=applicant_id, test_try=tries).last()

        return Response({"error": "Invalid passing the parameters"}, status=HTTP_400_BAD_REQUEST)