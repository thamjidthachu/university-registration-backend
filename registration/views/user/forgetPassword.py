from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.generics import GenericAPIView
from email_handling.views.body_mails import forgetPasswordMail
from ...models.applicant import Applicant
from tokens.views.tokenGenerator import token_generator
from registration.tasks import send_email
from django.conf import settings


class ForgetPassword(GenericAPIView):

    def post(self, request):

        applicant = self.check_applicant(self.request.data['email'], self.request.data['national_id'])
        if applicant.exists():
            app = applicant.last()
            token = token_generator.make_token({"pk": app.id,
                                        "username": "changePassword",
                                        "user_type": "change_password_" + str(app.id)
                                        })
            body = forgetPasswordMail()
            send_email.delay(self.request.META.get('HTTP_HOST'), app.first_name,
                             app.email, url=f"{settings.WEB_BASE_URL}/applicant/reset/password/token={token}",
                             english=body['english'], arabic=body['arabic'],
                             subject='AlMaarefa University Forgot Password', link="Reset Password")

            return Response("mail has been sent.", status=HTTP_200_OK)

        return Response("Invalid Email or national id", status=HTTP_400_BAD_REQUEST)

    def check_applicant(self, email, national_id):
        return Applicant.objects.filter(email__exact=email, national_id__exact=national_id)
