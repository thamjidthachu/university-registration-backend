from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR

from registration.models.user_model import User
from registration.serializers.admin.interviewGradeSerializer import InterviewSerializer, InterviewResultSerializer, \
    InterviewScoreSerializer
from registration.serializers.admin.englishGradeSerializer import EnglishSerializer
from registration.serializers.admin.admissionSerializer import FilesApplicantRetreiveSerializer
from email_handling.views.body_mails import interviewAbsentMail
from registration.models.evaluation import Interview, EnglishTest, Absent
from registration.models.applicant import Applicant, Files
from registration.tasks import send_email

from rest_framework.exceptions import NotFound


class InterviewSupervisor(GenericAPIView):
    serializer_class = InterviewSerializer

    def put(self, request, *args, **kwargs):
        try:
            userRole = self.get_user(int(self.request.session['user']['pk'])).role
            interview_result_id = self.request.query_params.get('id')
            if 'id' in self.request.query_params and userRole in (5, 13, 2, 90):
                serializer = InterviewScoreSerializer(
                    data=self.request.data) if userRole == 13 else InterviewResultSerializer(data=self.request.data)
                serializer.is_valid(raise_exception=True)
                interview_result = self.get_queryset(interview_result_id)
                if not interview_result:
                    raise NotFound("No Interview result found.")

                user = self.get_user(int(self.request.session['user']['pk']))
                serializer.update(interview_result, serializer.validated_data, user)

                if interview_result.result == "A":
                    body = interviewAbsentMail()
                    send_email.delay(self.request.META.get('HTTP_HOST'), interview_result.applicant_id.first_name,
                                    interview_result.applicant_id.email, interview_result.applicant_id.arabic_first_name,
                                    interview_result.applicant_id.gender, english=body['english'], arabic=body['arabic'],
                                    subject='AlMaarefa University Interview Result', link="الدخول لحسابك")

                    Absent.objects.create(applicant_id=Applicant.objects.get(id=interview_result_id),
                                        reservation_id=interview_result.reservation_id)
                    interview_result.reservation_id.count -= 1
                    interview_result.reservation_id.save()
                    interview_result.delete()

                return Response("Done", status=HTTP_200_OK)

            return Response({"error": "Invalid passing the parameters"}, status=HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": "Something went wrong","details":str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        try:
            interview_result_id = self.request.query_params.get('id')
            intr_object = self.get_queryset(interview_result_id)
            if not intr_object:
                raise NotFound("No Interview result found.")

            applicant = intr_object.applicant_id
            files = Files.objects.filter(applicant_id=applicant.id)
            interview = self.serializer_class(intr_object).data

            english_data = None
            english_logs = {}
            english = self.get_english_data(interview_result_id)
            if english:
                english_data = EnglishSerializer(english.last()).data
                english_dates = EnglishSerializer(english, many=True).data
                english_logs = {
                    "english_dates": english_dates,
                    "certificate_data": None,
                }
            if self.check_english_certf(applicant):
                english_logs['certificate_data'] = {
                    "score": applicant.english_certf_score if applicant.english_certf_score else 0,
                    "confirmed": applicant.english_certf_confirmation if applicant.english_certf_confirmation else False,
                    "state": applicant.english_certf_result if applicant.english_certf_result else None,
                    "university_certification": applicant.university_english_certification.url if applicant.university_english_certification else None ,
                }
                
            return Response({
                'applicant_id': interview.pop('applicant_id'),
                "reservation_id": interview.pop('reservation_id'),
                "id": interview,
                "english_data": english_data,
                "english_logs": english_logs,
                "files": FilesApplicantRetreiveSerializer(files, many=True).data,
            }, status=HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": "Something went wrong","details":str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


    def get_queryset(self, interview_result_id):
        try:
            return Interview.objects.get(applicant_id=interview_result_id)
        except Interview.DoesNotExist:
            return None

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def get_english_data(self, interview_result_id):
        try:
            return EnglishTest.objects.filter(applicant_id=interview_result_id).order_by('test_try')
        except EnglishTest.DoesNotExist:
            return None

    @staticmethod
    def check_english_certf(applicant):
        return isinstance(applicant.english_certf_score, float) and applicant.english_certf_score > 0

