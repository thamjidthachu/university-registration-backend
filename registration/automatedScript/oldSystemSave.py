from registration.models.applicant import Applicant
from rest_framework.generics import GenericAPIView
from django.http import HttpResponse
from email_handling.views.email_send import Mail
from email_handling.views.body_mails import oldsystemMail


class OldSystemRun(GenericAPIView):
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

    def post(self, request):
        import random
        for k in request.data:
            try:
                app = Applicant.objects.create(
                    application_no=random.randint(20000, 1000000000),
                    first_name=k['full_name'].split(" ")[0],
                    middle_name=k['full_name'].split(" ")[1],
                    full_name=k['full_name'],
                    arabic_full_name=k['arabic_full_name'],
                    gender=k['gender'],
                    phone=k['phone'],
                    email=k['email'],
                    national_id=k['national_id'],
                    nationality=k['nationality'],
                    birth_date=k['birth_date'],
                    apply_semester=k['apply_semester'],
                    high_school_GPA=k['university_gpa'],
                    high_graduation_year=k['university_year'],
                    qiyas_aptitude=k['qudurat'],
                    qiyas_achievement=k['tahsili'],
                    previous_GPA=float(k['previous_gpa']),
                    nationality_arabic=k['nationality_arabic'],
                    high_school_year=k['high_school_year'],
                    high_school_name=k['high_school_name'],
                    high_school_city=k['high_school_city'],
                    reference_name=k['reference_name'],
                    reference_phone=k['reference_phone'],
                    university_transfer=k['university_transfer'],
                    previous_university=k['previous_university'],
                    max_gpa=k['max_prev_gpa']

                )

                if app.email is not None and app.national_id not in self.exclude_applicants:
                    body = oldsystemMail(app)
                    Mail(request, app).send(
                        app.email,
                        english=body['english'],
                        arabic=body['arabic'],
                        subject='Al Maarefa University KSA Registration succeeded',
                        login="Login Now"
                    )

            except Exception as e:
                fn = open("log_old_system", "a+")
                fn.write(str(k['email']) + "  " + str(k['full_name']) + "  " + str(
                    e) + "\n<------------------------------------------------------------------------>\n")
                fn.close()
                continue
        return HttpResponse("Done")

    def get(self, request):
        return HttpResponse(Applicant.objects.all().count())