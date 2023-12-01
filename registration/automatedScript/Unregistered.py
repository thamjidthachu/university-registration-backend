from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.generics import GenericAPIView
from registration.models.applicant import Applicant
from sms.smsSend import SmsSend
from django.utils.timezone import datetime


class AutomatedSendSmsUnregistered(GenericAPIView):
    exclude_applicants = [
        2196242925,
        1113753212,
        1036913307,
        1097677247,
        1113222929,
        1111462444,
        3696231582,
        2206547966,
        1110426325,
        2208872248,
        2392219222,
        1118898889,
        1096669484,
        2184085591,
        1116903152,
        1116748516,
        1119429049,
        1118436508,
        1060307590,
        1097905192,
        1112525207,
        2208786208,
        1108075266,
        2204716571,
        2448068839,
        2182883187,
        2201688443,
        2193558778,
        1117165553,
        2201627003,
        1115450932,
        1104014301,
        1112729361,
        2185250897,
        1119429049,
        2183686969,
        1127648515,
        1097487977,
        2186974453,
        1102701610,
        2225293501,
        2190969663,
        1110783279,
        2271559136,
        2185817711,
        2225252358,
        2180017242,
        1115589788,
        1103412357,
        1121076796,
        2194852634,
        1081849158,
        1115436733,
        2203646985,
        2180709715,
        1117428019,
        1125526986,
        1115450932,
        2316783600,
        2183383633,
        1112066772,
        2191494125,
        1114077249,
        1105435463,
        1115812495,
        1109121648,
        2184085591,
        1113394769,
        1114630765,
        1090965656,
        2176492029,
        1114819756,
        2208872248,
        2201627003,
        1104014301,
        1081849158,
        1112026016,
        1119561445,
        1119094074,
        2326137995,
        2368458929,
        1116493535,
        2182347183,
        2328769530,
        1118452901,
        2188482794,
        2266664693,
        1095442297,
        2317892566,
        1108282805,
        2203215310,
        1119602025,
        1132823681,
        1123624296,
        1117554954,
        1116518927,
        2185250897,
        3696231582,
        1088932155,
        1091148690,
        1100604329,
        1048817447,
        2188422873,
        1109223170,
        2187428269,
        1110783279,
        2271559136,
        2185817711,
        2225252358,
        2180017242,
        1115589788,
        1103412357,
        1121076796,
        2194852634,
        1081849158,
        1115436733,
        2203646985,
        2180709715,
        1117428019,
        1125526986,
        2316783600,
        2183383633,
        1112066772,
        2191494125,
        1114077249,
        1105435463,
        1115812495,
        1109121648,
        2184085591,
        1113394769,
        1114630765,
        1090965656,
        2176492029,
        1114819756,
    ]

    def post(self, request, *args, **kwargs):
        applicants, last_id = self.get_queryset(self.request.data['last_id'])
        if applicants.exists():
            for app in applicants:
                if app.national_id not in self.exclude_applicants and app.phone is not None:
                    message = 'جامعة المعرفة الأهلية ترحب بك وتدعوك لإكمال التسجيل عبر منصة القبول على الرابط الآتي ' + ' https://my.um.edu.sa/auth/applicant/login'
                    message += '\nاسم المستخدم: ' + app.email + "\n الرقم السري: " + str(app.application_no)
                    try:
                        SmsSend().sendSingleNumber(app.phone, message)
                    except Exception as e:
                        pass
                    fn = open("log_sms_unregistered", "a+")
                    fn.write(
                        str(app.full_name) + " ----- has been Sent\n<------------------------------------------------------------------------>\n")
                    fn.close()
            return Response({
                "last_id": applicants[len(applicants) - 1].id,
                "total": last_id
            }, status=HTTP_200_OK)
        else:
            return Response("empty", status=HTTP_200_OK)

    def get_queryset(self, id):
        applicants = Applicant.objects.filter(init_state__isnull=True,
                                              email__isnull=False,
                                              id__gt=id,
                                              registration_date__lt=datetime.now().date(),
                                              accepted_outside=False).order_by('registration_date')
        if applicants.exists():
            return applicants[:5], applicants[len(applicants) - 1].id
        return applicants, 0
