from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from registration.models.applicant import Applicant, Files
from registration.models.evaluation import EnglishTest, Interview
from registration.serializers.admin.admissionSerializer import (
    ApplicantRetreiveSerializer, FilesApplicantRetreiveSerializer,
    FilesApplicantUpdateSerializer, ApplicantUpdateSerializer,
    ApplicantContactedSerializer, EnglishRetreiveSerializer,
    InterviewRetreiveSerializer, ApplicantPerioritiesSerializer,
    AdmissionListApplicant
)
from email_handling.views.body_mails import admissionMail
from registration.models.user_model import User
from registration.tasks import send_email


class AdmissionUpload(GenericAPIView):

    def put(self, request, *args, **kwargs):
        applicant = ApplicantUpdateSerializer(data=self.request.data['profile'])
        applicant.is_valid(raise_exception=True)
        app = self.get_applicant(self.request.data['profile']['id'])
        user = self.get_user(int(self.request.session['user']['pk']))
        applicant.update(app, self.request.data['profile'], user)
        reject_files = []
        for file in self.request.data['files']:
            update = FilesApplicantUpdateSerializer(data=file)
            update.is_valid(raise_exception=True)
            f = update.update(
                Files.objects.get(id=file['id']),
                file,
                user
            )
            if f.status == "RJ":
                reject_files.append(f.file_name.replace("_", " ") + " : " + f.rej_reason)
        body = admissionMail(app, tuple(reject_files))
        send_email.delay(
            self.request.META.get('HTTP_HOST'), app.first_name,
            app.email, app.arabic_first_name, app.gender, english=body['english'], arabic=body['arabic'],
            subject='Al Maarefa University Application Reviewed',
            login="الدخول لحسابك"
        )

        return Response("Done", status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        applicant_id = self.request.query_params.get('id')
        applicant = self.get_applicant(applicant_id)
        profile = ApplicantRetreiveSerializer(applicant).data
        files_applicant = self.get_files_applicant(applicant.id)
        files = []
        if files_applicant is not None:
            files = FilesApplicantRetreiveSerializer(files_applicant, many=True).data
        priorities = ApplicantPerioritiesSerializer(applicant).data
        english = {}
        interview = {}
        english_logs = {
            "english_dates": None,
            "certificate_data": None,
        }

        file_object = self.get_files_applicant(applicant.id).first()

        user_staff = None
        if file_object:
            try:
                user_staff = file_object.user.full_name
            except AttributeError:
                pass

        eng = self.get_english_test(applicant_id)
        intr = self.get_interview(applicant_id)
        if eng.exists():
            english = EnglishRetreiveSerializer(eng.last()).data
            english_dates = EnglishRetreiveSerializer(eng, many=True).data
            english_logs['english_dates'] = english_dates
        if self.check_english_certf(applicant):
            english_certificate_data = {
                "score": applicant.english_certf_score,
                "confirmed": applicant.english_certf_confirmation,
                "state": applicant.english_certf_result,
                "university_certification": applicant.university_english_certification.url if applicant.university_english_certification else None,
            }
            english_logs['certificate_data'] = english_certificate_data
        if intr.exists():
            interview = InterviewRetreiveSerializer(intr.last()).data
        return Response({"profile": profile,
                         "files": files,
                         "interview": interview,
                         "english": english,
                         "english_logs": english_logs,
                         "periorities": priorities,
                         "user_staff": user_staff,
                         "register_data": AdmissionListApplicant(applicant).data
                         }, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = self.get_user(int(self.request.session['user']['pk']))
        applicant = self.get_applicant(self.request.data['id'])
        applicant_data = ApplicantContactedSerializer(data=self.request.data, context={'user': user})
        applicant_data.is_valid(raise_exception=True)
        applicant_data.update(
            applicant,
            applicant_data.validated_data
        )
        return Response("Done", status=HTTP_200_OK)

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_applicant(applicant_id):
        try:
            return Applicant.objects.get(id=applicant_id)
        except Applicant.DoesNotExist:
            return None

    @staticmethod
    def get_files_applicant(applicant_id):
        try:
            files = Files.objects.filter(applicant_id=applicant_id)
        except:
            files = None
        return files

    @staticmethod
    def check_english_certf(applicant):
        if isinstance(applicant.english_certf_score, float) and applicant.english_certf_score > 0:
            return True
        return False

    @staticmethod
    def get_english_test(applicant_id):
        return EnglishTest.objects.filter(applicant_id_id=applicant_id).order_by('test_try')

    @staticmethod
    def get_interview(applicant_id):
        return Interview.objects.filter(applicant_id_id=applicant_id)
