from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST

from email_handling.views.body_mails import CertificateSubmissionMail
from registration.models.applicant import Applicant, Certificate
from registration.serializers.admin import CreateCertificateListSerializer
from registration.serializers.admin.certificateserializer import SubmitCertificateSerializer, \
    RetrieveCertificateSerializer
from registration.tasks import send_email


class CreateCertificateListView(CreateAPIView):

    def post(self, request, *args, **kwargs):
        try:
            applicant_id = self.request.data['id']
            for certificate in self.request.data['certificates']:
                data = {
                    "applicant": applicant_id,
                    "name": certificate
                }
                create_cert = CreateCertificateListSerializer(data=data)
                create_cert.is_valid(raise_exception=True)
                create_cert.create(create_cert.validated_data)
                Applicant.objects.filter(id=applicant_id).update(certificate_status='NS')

            return Response({"Success": "Successfully Created"}, status=HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitCertificateListView(RetrieveUpdateAPIView):

    def get(self, request, *args, **kwargs):
        applicant_id = self.request.query_params.get("id", None)
        certificates = Certificate.objects.filter(applicant_id=applicant_id)
        certificates_data = RetrieveCertificateSerializer(certificates, many=True)
        return Response({
            "data": certificates_data.data
        })

    def put(self, request, *args, **kwargs):
        try:
            if {'id', 'certificates', 'certificate_status'} <= request.data.keys():
                applicant_id = self.request.data['id']
                applicant = Applicant.objects.get(id=applicant_id)
                user = self.request.session['user']['pk']
                certificates = self.request.data['certificates']
                for certificate in certificates:
                    data = {
                        "status": True,
                        "approve_user": user
                    }
                    cert_submission = SubmitCertificateSerializer(data=data)
                    cert_submission.is_valid(raise_exception=True)
                    cert = Certificate.objects.get(applicant=applicant_id, name=certificate)
                    cert_submission.update(cert, cert_submission.validated_data)

                to_submit = Certificate.objects.filter(applicant=applicant_id, status=False).exclude(
                    applicant=applicant_id, name__in=certificates).values_list('name', flat=True)
                Applicant.objects.filter(id=applicant_id).update(
                    certificate_status=self.request.data['certificate_status'])
                body = CertificateSubmissionMail(certificates, list(to_submit))
                send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                           applicant.email, applicant.arabic_first_name, applicant.gender,
                           english=body['english'], arabic=body['arabic'],
                           subject='Al Maarefa University Certificate Received')

                return Response({"Success": "Successfully Updated"}, status=HTTP_200_OK)
            else:
                return Response({"Error": "Invalid Keys Passed", "warning_ar": "تم تمرير مفاتيح غير صالحة "},
                                status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
