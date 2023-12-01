from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from sms.smsSend import SmsSend
from ....models.applicant import Applicant


class SendCustomSms(CreateAPIView):
    def post(self, request, *args, **kwargs):
        if request.data and {"message", "applicants"} <= request.data.keys():
            message = str(request.data['message'])
            for app in request.data['applicants']:
                if not self.get_applicant(app['id']).phone.startswith('966'):
                    continue
                elif self.request.query_params['send_to'] == 'superior':
                    phone = self.get_applicant(app['id']).superior_phone  # superior phone

                else:
                    phone = self.get_applicant(app['id']).phone  # applicant phone
                try:
                    SmsSend().sendSingleNumber(phone, message)
                except:
                    return Response({"ERROR": "invalid Phone Number", "ERROR_ar": "رقم تليفون خاطئ"},
                                    status=HTTP_400_BAD_REQUEST)
            return Response({"Success": "Successfully sent"}, status=HTTP_200_OK)
        else:
            return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)

    @staticmethod
    def get_applicant(applicant_id):
        return Applicant.objects.get(id=applicant_id)
