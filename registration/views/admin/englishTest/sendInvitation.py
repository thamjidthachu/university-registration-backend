from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from email_handling.views.body_mails import englishSendInvitationMail, interviewSendInvitationMail
from ....models.evaluation import EnglishTest, Interview
from registration.tasks import send_email
from sms.smsSend import SmsSend

import logging
import re
import requests
import json

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename="action.log",
                    format='%(asctime)s %(message)s',
                    )
# create object from logging
logger = logging.getLogger(__name__)

# set logging debug
logger.setLevel(logging.DEBUG)

pattern = r'''^(http(s)?:\/\/)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$'''


class SendInvitation(CreateAPIView):

    def post(self, request, *args, **kwargs):
        if 'link' in self.request.data:
            if not re.match(pattern, self.request.data['link']):
                return Response({"error": "Invalid passing url", "error_ar": "تاكد من ادخال الرابط بشكل صحيح"},
                                status=HTTP_400_BAD_REQUEST)

            applicants = self.get_applicant(self.request.data['ids'], self.request.data['test_type'])

            if applicants is None:
                return Response({"ERROR": "Invalid Test Type", "ERROR_ar": "نوع الامتحان غير صالح"},
                                status=HTTP_404_NOT_FOUND)

            if applicants.exists():
                short_link = self.make_shortener(self.request.data['link'])
                if self.request.data['test_type'] == "1":
                    body = englishSendInvitationMail()
                    message = "نشكرك لاختيارك جامعة المعرفة" + \
                              "\nالرجاء العلم انه بإمكانك بدء اختبار اللغه من خلال زياره الرابط التالي" + \
                              "\n" + short_link + "\n" + \
                              "نتمنى لك التوفيق"
                else:
                    body = interviewSendInvitationMail()
                    message = "نشكرك لاختيارك جامعة المعرفة" + \
                              "\nالرجاء العلم انه بإمكانك بدء اختبار المقابلة من خلال زياره الرابط التالي" + \
                              "\n" + short_link + "\n" + \
                              "نتمنى لك التوفيق"

                for applicant in applicants:
                    applicant = applicant.applicant_id
                    send_email.delay(self.request.META.get('HTTP_HOST'), applicant.first_name,
                                     applicant.email, applicant.arabic_first_name, applicant.gender,
                                     url=self.request.data['link'],
                                     english=body['english'], arabic=body['arabic'],
                                     subject='Al Maarefa University KSA Send Invitation', additional_link="Click Here")
                    logger.info('User : ' + str(self.get_user_name(int(self.request.session['user']['pk']))) + ' sent the invitation link to the applicant ' + str(applicant.arabic_full_name) )
                    try:
                        SmsSend().sendSingleNumber(applicant.phone, message)
                    except Exception as e:
                        pass
                return Response("Successfully sent", status=HTTP_200_OK)

            return Response({"ERROR": "This applicant doesn't exist", "warning_ar": "لا يوجد طلاب"},
                            status=HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid passing the parameters"}, status=HTTP_400_BAD_REQUEST)

    def get_applicant(self, ids, test_type):

        if test_type == "1":
            return EnglishTest.objects.filter(applicant_id_id__in=ids)

        elif test_type == "2":
            return Interview.objects.filter(applicant_id_id__in=ids)

        return

    def get_user_name(self, user_id):
        from ....models.user_model import User
        return User.objects.get(id=user_id).full_name

    def make_shortener(self, link):
        if not link.startswith("https://"):
            link = "https://" + link

        linkRequest = {
            "destination": link
            , "domain": {"fullName": "rebrand.ly"}
        }
        requestHeaders = {
            "Content-type": "application/json",
            "apikey": "d8650f27f27a4b88bd56806a41d609c4",
        }

        r = requests.post("https://api.rebrandly.com/v1/links",
                          data=json.dumps(linkRequest),
                          headers=requestHeaders)

        if (r.status_code == requests.codes.ok):
            link = r.json()

            return link["shortUrl"]
