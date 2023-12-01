from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from equations.models.equations import Equation
from equations.models.services import Service
from equations.serializers.equationSerializer import ListEquationsSerializer
from registration.models.applicant import Applicant, Payment
from registration.models.applicant import Files
from registration.models.evaluation import EnglishTest, Reservation
from registration.models.evaluation import Interview
from registration.models.sysadmin import UnivPayments
from registration.models.univStructure import Major
from registration.models.user_model import User
from registration.serializers.admin.admissionSerializer import MajorListSerializer, RoleListSerializer
from registration.serializers.user.paymentSerializer import PayGetSerializer
from registration.serializers.user.uploadSerializer import FileSerializer

import logging

logger = logging.getLogger('root')


class currentUserInfo(GenericAPIView):

    def get(self, request, *args, **kwargs):
        user = self.request.session['user']
        app = self.get_applicant_user(int(user['pk']), user['user_type'])
        if user['user_type'] == 'applicant':
            return self.get_applicant_data(app)
        else:
            return Response({
                "id": app.id,
                "full_name": app.full_name,
                "role": app.role,
                "gender": app.gender,
                "email": app.email,
                "Phone": app.Phone,
                "user_major": app.user_major if app.user_major else "all",
                "statistics": self.statistics(app.role, self.request.query_params['semester'], app.user_major),
                "majors": MajorListSerializer(Major.objects.all(), many=True).data,
                "signature": str(app.signature),
                "user_roles": RoleListSerializer(app.user_roles.all(), many=True).data
            }, status=HTTP_200_OK)

    @staticmethod
    def statistics(role, semester, user_major):
        result = {}

        if role == 5:  # Supervisor Department
            interviewAllApplicants = Interview.objects.filter(
                applicant_id__apply_semester=semester,
                applicant_id__major_id__faculty_id__name=user_major
            ).count()
            interview_not_graded = Interview.objects.filter(result__isnull=True, applicant_id__apply_semester=semester,
                                                            applicant_id__major_id__faculty_id__name=user_major).count()
            interviewSuccess = Interview.objects.filter(result='S', applicant_id__apply_semester=semester,
                                                        applicant_id__major_id__faculty_id__name=user_major).count()
            interviewFail = Interview.objects.filter(result='F', applicant_id__apply_semester=semester,
                                                     applicant_id__major_id__faculty_id__name=user_major).count()
            interviewPostponed = Interview.objects.filter(result='P', applicant_id__apply_semester=semester,
                                                          applicant_id__major_id__faculty_id__name=user_major).count()
            interviewAbsent = Interview.objects.filter(result='A', applicant_id__apply_semester=semester,
                                                       applicant_id__major_id__faculty_id__name=user_major).count()
            interviewLowScore = Interview.objects.filter(result='L', applicant_id__apply_semester=semester,
                                                         applicant_id__major_id__faculty_id__name=user_major).count()
            result.update({"interviewAllApplicants": interviewAllApplicants,
                           "interview_not_graded": interview_not_graded,
                           "interviewSuccess": interviewSuccess,
                           "interviewFail": interviewFail,
                           "interviewPostponed": interviewPostponed,
                           "interviewAbsent": interviewAbsent,
                           "interviewLowScore": interviewLowScore})

        if role == 4:  # Scholarships Department
            Paid_ERET_all = Payment.objects.filter(payment_id__payment_title="ERET",
                                                   applicant_id__apply_semester=semester).count()
            Paid_ERET_S = Payment.objects.filter(paid=True, payment_id__payment_title="ERET",
                                                 applicant_id__apply_semester=semester).count()
            Paid_ERET_F = Payment.objects.filter(paid=False, payment_id__payment_title="ERET",
                                                 applicant_id__apply_semester=semester).count()

            Paid_REG_all = Payment.objects.filter(payment_id__payment_title="REG",
                                                  applicant_id__apply_semester=semester).count()
            Paid_REG_S = Payment.objects.filter(paid=True, payment_id__payment_title="REG",
                                                applicant_id__apply_semester=semester).count()
            Paid_REG_F = Payment.objects.filter(paid=False, payment_id__payment_title="REG",
                                                applicant_id__apply_semester=semester).count()

            Paid_REG_MS = Payment.objects.filter(paid=True, applicant_id__major_id__name='MS',
                                                 payment_id__payment_title="REG",
                                                 applicant_id__apply_semester=semester).count()
            Paid_REG_PHD = Payment.objects.filter(paid=True, applicant_id__major_id__name='PHD',
                                                  payment_id__payment_title="REG",
                                                  applicant_id__apply_semester=semester).count()
            Paid_REG_NU = Payment.objects.filter(paid=True, applicant_id__major_id__name='NU',
                                                 payment_id__payment_title="REG",
                                                 applicant_id__apply_semester=semester).count()
            Paid_REG_RT = Payment.objects.filter(paid=True, applicant_id__major_id__name='RT',
                                                 payment_id__payment_title="REG",
                                                 applicant_id__apply_semester=semester).count()
            Paid_REG_EMS = Payment.objects.filter(paid=True, applicant_id__major_id__name='EMS',
                                                  payment_id__payment_title="REG",
                                                  applicant_id__apply_semester=semester).count()
            Paid_REG_AT = Payment.objects.filter(paid=True, applicant_id__major_id__name='AT',
                                                 payment_id__payment_title="REG",
                                                 applicant_id__apply_semester=semester).count()
            Paid_REG_HIS = Payment.objects.filter(paid=True, applicant_id__major_id__name='HIS',
                                                  payment_id__payment_title="REG",
                                                  applicant_id__apply_semester=semester).count()
            Paid_REG_IS = Payment.objects.filter(paid=True, applicant_id__major_id__name='IS',
                                                 payment_id__payment_title="REG",
                                                 applicant_id__apply_semester=semester).count()
            Paid_REG_CS = Payment.objects.filter(paid=True, applicant_id__major_id__name='CS',
                                                 payment_id__payment_title="REG",
                                                 applicant_id__apply_semester=semester).count()
            Paid_REG_IE = Payment.objects.filter(paid=True, applicant_id__major_id__name='IE',
                                                 payment_id__payment_title="REG",
                                                 applicant_id__apply_semester=semester).count()
            Paid_REG_GSE = Payment.objects.filter(paid=True, applicant_id__major_id__name='GSE',
                                                  payment_id__payment_title="REG",
                                                  applicant_id__apply_semester=semester).count()
            result.update({"Paid_ERET_all": Paid_ERET_all, "Paid_REG_all": Paid_REG_all, "Paid_ERET_S": Paid_ERET_S,
                           "Paid_ERET_F": Paid_ERET_F, "Paid_REG_S": Paid_REG_S, "Paid_REG_F": Paid_REG_F,
                           "Paid_REG_MS": Paid_REG_MS, "Paid_REG_PHD": Paid_REG_PHD, "Paid_REG_NU": Paid_REG_NU,
                           "Paid_REG_RT": Paid_REG_RT, "Paid_REG_EMS": Paid_REG_EMS, "Paid_REG_AT": Paid_REG_AT,
                           "Paid_REG_HIS": Paid_REG_HIS, "Paid_REG_IS": Paid_REG_IS, "Paid_REG_CS": Paid_REG_CS,
                           "Paid_REG_IE": Paid_REG_IE, "Paid_REG_GSE": Paid_REG_GSE})

        elif role == 3:  # English Department
            EnglishAllApplicants = EnglishTest.objects.filter(applicant_id__apply_semester=semester).count()
            EnglishNotGraded = EnglishTest.objects.filter(result__isnull=True,
                                                          applicant_id__apply_semester=semester).count()
            EnglishSuccess = EnglishTest.objects.filter(result='S', applicant_id__apply_semester=semester).count()
            EnglishFail = EnglishTest.objects.filter(result='F', applicant_id__apply_semester=semester).count()
            EnglishPostponed = EnglishTest.objects.filter(result='P', applicant_id__apply_semester=semester).count()
            EnglishAbsent = EnglishTest.objects.filter(result='A', applicant_id__apply_semester=semester).count()
            EnglishLowScore = EnglishTest.objects.filter(result='L', applicant_id__apply_semester=semester).count()
            reg_Cert_Res_S = Applicant.objects.filter(english_certf_result='S', apply_semester=semester).count()
            reg_Cert_Res_F = Applicant.objects.filter(english_certf_result='F', apply_semester=semester).count()
            result.update({"EnglishAllApplicants": EnglishAllApplicants,
                           "EnglishNotGraded": EnglishNotGraded,
                           "EnglishSuccess": EnglishSuccess,
                           "EnglishFail": EnglishFail,
                           "EnglishPostponed": EnglishPostponed,
                           "EnglishAbsent": EnglishAbsent, "EnglishLowScore": EnglishLowScore,
                           "reg_Cert_Res_S": reg_Cert_Res_S, "reg_Cert_Res_F": reg_Cert_Res_F})
        # roles in [Admission Department, Register Review, Admission Manager,Registration]
        elif role in [2, 11, 6, 16]:
            reg_all = Applicant.objects.filter(init_state__isnull=False, apply_semester=semester).count()
            reg_arabic_speakers = Applicant.objects.filter(init_state__isnull=False, apply_semester=semester,
                                                           arabic_speaker=False).count()
            reg_UR = Applicant.objects.filter(init_state='UR', apply_semester=semester).count()
            reg_Un_registered = Applicant.objects.filter(init_state__isnull=True, apply_semester=semester).count()
            reg_IA = Applicant.objects.filter(init_state='IA', apply_semester=semester).count()
            reg_CA = Applicant.objects.filter(init_state='CA', apply_semester=semester).count()
            reg_RJ = Applicant.objects.filter(init_state='RJ', apply_semester=semester).count()
            reg_CONTACT = Applicant.objects.filter(contacted=True, apply_semester=semester).count()
            reg_NOT_CONTACT = Applicant.objects.filter(contacted=False, apply_semester=semester).count()
            reg_contact_attend = Applicant.objects.filter(contact_result='WA', apply_semester=semester).count()
            reg_contact_no_reply = Applicant.objects.filter(contact_result='NR', apply_semester=semester).count()
            reg_contact_withdraw_reg = Applicant.objects.filter(contact_result='WR', apply_semester=semester).count()
            reg_contact_maj_medicine = Applicant.objects.filter(contact_result='MM', apply_semester=semester).count()
            student_id_saudi = Applicant.objects.filter(student_id__isnull=False, national_id__startswith="1",
                                                        apply_semester=semester).count()
            student_id_no_saudi = Applicant.objects.filter(
                Q(student_id__isnull=False) & ~Q(national_id__startswith="1"), apply_semester=semester).count()
            final_state_accepted = Applicant.objects.filter(final_state__exact="A", apply_semester=semester).count()
            final_state_accepted_MS = Applicant.objects.filter(final_state__exact="A", major_id__name='MS',
                                                               apply_semester=semester).count()
            final_state_accepted_PHD = Applicant.objects.filter(final_state__exact="A", major_id__name='PHD',
                                                                apply_semester=semester).count()
            final_state_accepted_NU = Applicant.objects.filter(final_state__exact="A", major_id__name='NU',
                                                               apply_semester=semester).count()
            final_state_accepted_RT = Applicant.objects.filter(final_state__exact="A", major_id__name='RT',
                                                               apply_semester=semester).count()
            final_state_accepted_EMS = Applicant.objects.filter(final_state__exact="A", major_id__name='EMS',
                                                                apply_semester=semester).count()
            final_state_accepted_AT = Applicant.objects.filter(final_state__exact="A", major_id__name='AT',
                                                               apply_semester=semester).count()
            final_state_accepted_HIS = Applicant.objects.filter(final_state__exact="A", major_id__name='HIS',
                                                                apply_semester=semester).count()
            final_state_accepted_IS = Applicant.objects.filter(final_state__exact="A", major_id__name='IS',
                                                               apply_semester=semester).count()
            final_state_accepted_CS = Applicant.objects.filter(final_state__exact="A", major_id__name='CS',
                                                               apply_semester=semester).count()
            final_state_accepted_IE = Applicant.objects.filter(final_state__exact="A", major_id__name='IE',
                                                               apply_semester=semester).count()
            final_state_accepted_GSE = Applicant.objects.filter(final_state__exact="A", major_id__name='GSE',
                                                                apply_semester=semester).count()
            final_state_rejected = Applicant.objects.filter(final_state__exact="RJ", apply_semester=semester).count()
            interview_pass = Interview.objects.filter(result__exact="S", applicant_id__apply_semester=semester).count()
            interview_fail = Interview.objects.filter(result__exact="F", applicant_id__apply_semester=semester).count()
            english_fail = EnglishTest.objects.filter(result__exact="F", applicant_id__apply_semester=semester).count()
            english_pass = EnglishTest.objects.filter(result__exact="S", applicant_id__apply_semester=semester).count()
            total_applicants = Applicant.objects.filter(apply_semester=semester, major_id__name=user_major).count()
            total_female_applicants = Applicant.objects.filter(gender__exact="F", apply_semester=semester,
                                                               major_id__name=user_major).count()
            total_male_applicants = Applicant.objects.filter(gender__exact="M", apply_semester=semester,
                                                             major_id__name=user_major).count()
            result.update({
                "reg_All": reg_all,
                "reg_arabic_speakers": reg_arabic_speakers,
                "reg_Un_registered": reg_Un_registered,
                "reg_UR": reg_UR,
                "reg_IA": reg_IA,
                "reg_CA": reg_CA,
                "reg_RJ": reg_RJ,
                "reg_CO": reg_CONTACT,
                "reg_NOT_CO": reg_NOT_CONTACT,
                "reg_contact_attend": reg_contact_attend,
                "reg_contact_no_reply": reg_contact_no_reply,
                "reg_contact_withdraw_reg": reg_contact_withdraw_reg,
                "reg_contact_maj_medicine": reg_contact_maj_medicine,
                "student_id_saudi": student_id_saudi,
                "student_id_no_saudi": student_id_no_saudi,
                "final_state_accepted": final_state_accepted,
                "final_state_rejected": final_state_rejected,
                "interview_pass": interview_pass,
                "interview_fail": interview_fail,
                "english_pass": english_pass,
                "english_fail": english_fail,
                "final_state_accepted_MS": final_state_accepted_MS,
                "final_state_accepted_PHD": final_state_accepted_PHD,
                "final_state_accepted_NU": final_state_accepted_NU,
                "final_state_accepted_RT": final_state_accepted_RT,
                "final_state_accepted_EMS": final_state_accepted_EMS,
                "final_state_accepted_AT": final_state_accepted_AT,
                "final_state_accepted_HIS": final_state_accepted_HIS,
                "final_state_accepted_IS": final_state_accepted_IS,
                "final_state_accepted_CS": final_state_accepted_CS,
                "final_state_accepted_IE": final_state_accepted_IE,
                "final_state_accepted_GSE": final_state_accepted_GSE,
                "total_applicants": total_applicants,
                "total_female_applicants": total_female_applicants,
                "total_male_applicants": total_male_applicants
            })
        elif role == 7:  # Pharmacy Dean
            Dean_All_PH = Applicant.objects.filter(final_state__isnull=False, major_id__name='PHD',
                                                   apply_semester=semester).count()
            Dean_AC_PH = Applicant.objects.filter(final_state='A', major_id__name='PHD',
                                                  apply_semester=semester).count()
            Dean_RJ_PH = Applicant.objects.filter(final_state='RJ', major_id__name='PHD',
                                                  apply_semester=semester).count()
            Dean_RJM_PH = Applicant.objects.filter(final_state='RJM', major_id__name='PHD',
                                                   apply_semester=semester).count()
            Dean_W_PH = Applicant.objects.filter(final_state='W', major_id__name='PHD', apply_semester=semester).count()

            result.update({
                "Dean_All": Dean_All_PH,
                "Dean_AC": Dean_AC_PH,
                "Dean_RJ": Dean_RJ_PH,
                "Dean_RJM": Dean_RJM_PH,
                "Dean_W": Dean_W_PH
            })

        elif role == 9:  # Medicine Dean
            Dean_All_MS = Applicant.objects.filter(final_state__isnull=False, major_id__name='MS',
                                                   apply_semester=semester).count()
            Dean_AC_MS = Applicant.objects.filter(final_state='A', major_id__name='MS', apply_semester=semester).count()
            Dean_RJ_MS = Applicant.objects.filter(final_state='RJ', major_id__name='MS',
                                                  apply_semester=semester).count()
            Dean_RJM_MS = Applicant.objects.filter(final_state='RJM', major_id__name='MS',
                                                   apply_semester=semester).count()
            Dean_W_MS = Applicant.objects.filter(final_state='W', major_id__name='MS', apply_semester=semester).count()

            result.update({
                "Dean_All": Dean_All_MS,
                "Dean_AC": Dean_AC_MS,
                "Dean_RJ": Dean_RJ_MS,
                "Dean_RJM": Dean_RJM_MS,
                "Dean_W": Dean_W_MS
            })

        elif role == 10:  # Science Dean
            Dean_All_AS = Applicant.objects.filter(final_state__isnull=False,
                                                   major_id__name__in=['NU', 'RT', 'EMS', 'AT', 'HIS', 'IS', 'CS', 'IE',
                                                                       'GSE'], apply_semester=semester).count()
            Dean_AC_AS = Applicant.objects.filter(final_state='A',
                                                  major_id__name__in=['NU', 'RT', 'EMS', 'AT', 'HIS', 'IS', 'CS', 'IE',
                                                                      'GSE'], apply_semester=semester).count()
            Dean_RJ_AS = Applicant.objects.filter(final_state='RJ',
                                                  major_id__name__in=['NU', 'RT', 'EMS', 'AT', 'HIS', 'IS', 'CS', 'IE',
                                                                      'GSE'], apply_semester=semester).count()
            Dean_RJM_AS = Applicant.objects.filter(final_state='RJM',
                                                   major_id__name__in=['NU', 'RT', 'EMS', 'AT', 'HIS', 'IS', 'CS', 'IE',
                                                                       'GSE'], apply_semester=semester).count()
            Dean_W_AS = Applicant.objects.filter(final_state='W',
                                                 major_id__name__in=['NU', 'RT', 'EMS', 'AT', 'HIS', 'IS', 'CS', 'IE',
                                                                     'GSE'], apply_semester=semester).count()
            Dean_AC_NU = Applicant.objects.filter(final_state='A', major_id__name='NU', apply_semester=semester).count()
            Dean_AC_RT = Applicant.objects.filter(final_state='A', major_id__name='RT', apply_semester=semester).count()
            Dean_AC_EMS = Applicant.objects.filter(final_state='A', major_id__name='EMS',
                                                   apply_semester=semester).count()
            Dean_AC_AT = Applicant.objects.filter(final_state='A', major_id__name='AT', apply_semester=semester).count()
            Dean_AC_HIS = Applicant.objects.filter(final_state='A', major_id__name='HIS',
                                                   apply_semester=semester).count()
            Dean_AC_IS = Applicant.objects.filter(final_state='A', major_id__name='IS', apply_semester=semester).count()
            Dean_AC_CS = Applicant.objects.filter(final_state='A', major_id__name='CS', apply_semester=semester).count()
            Dean_AC_IE = Applicant.objects.filter(final_state='A', major_id__name='IE', apply_semester=semester).count()
            Dean_AC_GSE = Applicant.objects.filter(final_state='A', major_id__name='GSE',
                                                   apply_semester=semester).count()

            result.update({
                "Dean_All": Dean_All_AS,
                "Dean_AC": Dean_AC_AS,
                "Dean_RJ": Dean_RJ_AS,
                "Dean_RJM": Dean_RJM_AS,
                "Dean_W": Dean_W_AS,
                "Dean_AC_NU": Dean_AC_NU, "Dean_AC_RT": Dean_AC_RT, "Dean_AC_EMS": Dean_AC_EMS,
                "Dean_AC_AT": Dean_AC_AT,
                "Dean_AC_HIS": Dean_AC_HIS, "Dean_AC_IS": Dean_AC_IS, "Dean_AC_CS": Dean_AC_CS,
                "Dean_AC_IE": Dean_AC_IE, "Dean_AC_GSE": Dean_AC_GSE
            })

        elif role == 12:  # English Conformer
            result.update({
                "english_not_greaded": EnglishTest.objects.filter(result="S", confirmed__isnull=True,
                                                                  applicant_id__apply_semester=semester).count(),
                "english_greaded": EnglishTest.objects.filter(result="S", confirmed__isnull=False,
                                                              applicant_id__apply_semester=semester).count(),
                "all_english": EnglishTest.objects.filter(result="S", applicant_id__apply_semester=semester).count(),
            })
        elif role == 13:  # Interview Test
            interviewTest_All = Interview.objects.filter(applicant_id__apply_semester=semester).count()
            interviewTest_not_graded = Interview.objects.filter(result__isnull=True,
                                                                applicant_id__apply_semester=semester).count()
            interviewTest_AC = Interview.objects.filter(result='S', applicant_id__apply_semester=semester).count()
            interviewTest_RJ = Interview.objects.filter(result='F', applicant_id__apply_semester=semester).count()
            interviewTest_Postponed = Interview.objects.filter(result='P',
                                                               applicant_id__apply_semester=semester).count()
            interviewTest_Absent = Interview.objects.filter(result='A', applicant_id__apply_semester=semester).count()
            interviewTest_LowScore = Interview.objects.filter(result='L', applicant_id__apply_semester=semester).count()

            result.update({"interviewTest_All": interviewTest_All,
                           "interviewTest_not_graded": interviewTest_not_graded,
                           "interviewTest_AC": interviewTest_AC,
                           "interviewTest_RJ": interviewTest_RJ,
                           "interviewTest_Postponed": interviewTest_Postponed,
                           "interviewTest_Absent": interviewTest_Absent,
                           "interviewTest_LowScore": interviewTest_LowScore})
        elif role == 14:  # Equation Supervisor
            Equations_All = Equation.objects.filter(applicant__apply_semester=semester,
                                                    applicant__major_id__name=user_major).count()
            Equations_Pending_review = Equation.objects.filter(applicant__apply_semester=semester,
                                                               applicant__major_id__name=user_major).exclude(
                final_state='AC').count()
            Equations_pending_confirm = Equation.objects.filter(applicant__apply_semester=semester, final_state='AC',
                                                                confirmed=False,
                                                                applicant__major_id__name=user_major).count()
            Equations_confirmed = Equation.objects.filter(applicant__apply_semester=semester,
                                                          confirmed=True, applicant__major_id__name=user_major).count()

            result.update({
                "equations_all": Equations_All,
                "equations_pending_review": Equations_Pending_review,
                "equations_pending_confirm": Equations_pending_confirm,
                "equations_confirmed": Equations_confirmed
            })

        elif role == 15:  # Head Of Department
            Equations_All = Equation.objects.filter(applicant__apply_semester=semester,
                                                    applicant__major_id__name=user_major, ).count()
            Equations_Pending_review = Equation.objects.filter(applicant__apply_semester=semester,
                                                               applicant__major_id__name=user_major, init_state='AC',
                                                               head_of_department_state__isnull=True).count()
            Equations_pending_confirm = Equation.objects.filter(applicant__apply_semester=semester,
                                                                applicant__major_id__name=user_major, final_state='AC',
                                                                confirmed=False).count()
            Equations_confirmed = Equation.objects.filter(applicant__apply_semester=semester,
                                                          applicant__major_id__name=user_major,
                                                          confirmed=True, ).count()

            result.update({
                "equations_all": Equations_All,
                "equations_pending_review": Equations_Pending_review,
                "equations_pending_confirm": Equations_pending_confirm,
                "equations_confirmed": Equations_confirmed
            })

        return result

    @staticmethod
    def get_applicant_user(appId, user_type):
        try:
            if user_type == "applicant":
                return Applicant.objects.get(id=appId)
            else:
                return User.objects.get(id=appId)
        except Applicant.DoesNotExist or User.DoesNotExist:
            return None

    @staticmethod
    def get_files_applicant(applicant_id):
        try:
            return Files.objects.filter(applicant_id=applicant_id)
        except ObjectDoesNotExist:
            return None

    def get_applicant_data(self, applicant):
        docs_state, files = self.prepare_file_applicant(applicant.id)
        docs_state, english_date, english_grade = self.prepare_english_test_applicant(applicant, docs_state)
        interview_grade, interview_date = self.prepare_interview_test_applicant(applicant.id)
        major = Major.objects.filter(id=applicant.major_id_id)

        type_payment = None
        equ_payment = None
        major_res = None
        major_name = None
        pay = {}
        if len(english_date) > 1:
            if english_date[-1].get('state') == "F" and english_date[0].get('num_tries') > 1:
                type_payment = "ERET"

        if applicant.offer is not None and applicant.offer == "AC":
            type_payment = "REG"

        if applicant.init_state in ['IA', 'CA']:
            equ_payment = "EQU"

        if type_payment is not None:

            paymentCost = UnivPayments.objects.get(payment_title=type_payment)
            payment = Payment.objects.filter(applicant_id=applicant.id, payment_id__payment_title=type_payment)
            paid = False
            if payment.exists():
                paid = payment.last().paid

            if type_payment == "ERET":
                pay["retest"] = {
                    "cost": paymentCost.cost,
                    "paid": paid
                }

            elif type_payment == "REG":
                pay["register"] = {
                    "cost": paymentCost.cost,
                    "paid": paid
                }
        if equ_payment is not None:
            paymentCost = UnivPayments.objects.get(payment_title=equ_payment)
            payment = Payment.objects.filter(applicant_id=applicant.id, payment_id__payment_title=equ_payment)
            paid = False
            if payment.exists():
                paid = payment.last().paid

            pay["equation"] = {
                "cost": paymentCost.cost,
                "paid": paid
            }

        if major.exists():
            major_res = major.first().id
            major_name = major.first().name

        response = {
            "id": applicant.id,
            "full_name": applicant.full_name,
            "arabic_full_name": applicant.arabic_full_name,
            "national_id": applicant.national_id,
            "pledge": applicant.pledge,
            "student_id": applicant.student_id,
            "apply_semester": applicant.apply_semester,
            "init_state": applicant.init_state,
            "final_state": applicant.final_state,
            "email": applicant.email,
            "major": major_res,
            "major_name": major_name,
            "qudrat": applicant.qiyas_aptitude,
            "tahsily": applicant.qiyas_achievement,
            "GPA": applicant.previous_GPA,
            "high_school": applicant.high_school_GPA,
            "max_gpa": applicant.max_gpa,
            "payment": pay,
            "first_login": False if applicant.password else True,
            "first_periority": applicant.first_periority,
            "second_periority": applicant.second_periority,
            "third_periority": applicant.third_periority,
            "fourth_periority": applicant.fourth_periority,
            "fifth_periority": applicant.fifth_periority,
            "sixth_periority": applicant.sixth_periority,
            "seventh_periority": applicant.seventh_periority,
            "eighth_periority": applicant.eighth_periority,
            "ninth_periority": applicant.ninth_periority,
            "tenth_periority": applicant.tenth_periority,
            "phone": applicant.phone,
            "offer": applicant.offer,
            "gender": applicant.gender,
            "accepted_outside": applicant.accepted_outside,
            "role": 1,
            "docs_state": docs_state,
            "files": files,
            "majors": MajorListSerializer(Major.objects.all(), many=True).data,
            "english_certf_result": applicant.english_certf_result,
            "grade": {
                "eng": english_grade,
                "intr": interview_grade
            },
            "test": {
                "eng": english_date,
                "intr": interview_date,
            },
            "tagseer_department": applicant.tagseer_department,
            "secondary_type": applicant.secondary_type,
            'employment_state': applicant.employment_state,
            'applicant_type': applicant.applicant_type,
            'equation_fees_exempt': applicant.equation_fees_exempt,
            "equation": ListEquationsSerializer(Equation.objects.filter(applicant=applicant), many=True).data,
            "equation_status": Service.objects.get(name='EQU').active
        }
        payment = Payment.objects.filter(applicant_id_id=applicant.id, by_cash=True, paid=False)
        if payment.exists():
            data = PayGetSerializer(payment, many=True).data
            response['payment_by_cash'] = data

        return Response(response, status=HTTP_200_OK)

    def prepare_file_applicant(self, applicant_id):
        files = []
        docs_state = None
        files_list = self.get_files_applicant(applicant_id)
        for f in files_list:
            file = FileSerializer(f).data
            files.append(file)
            if docs_state != "rejected":
                if file['status'] == "RJ":
                    docs_state = "rejected"
                elif file['status'] == "A":
                    docs_state = "accepted"
                else:
                    docs_state = "uploaded"
        return docs_state, files

    def prepare_english_test_applicant(self, applicant, docs_state):
        english_date = []
        english_grade = []

        appEng = EnglishTest.objects.filter(applicant_id=applicant.id).order_by('id')

        if self.check_english_certf(applicant):
            english_grade.append({
                "score": applicant.english_certf_score,
                "confirmed": applicant.english_certf_confirmation,
                "state": applicant.english_certf_result
            })

        if appEng.count() > 0:
            english_date.append({"num_tries": appEng.count()})

            for app in appEng:
                date = Reservation.objects.get(id=app.reservation_id.id)
                english_date.append({
                    "date": date.reservation_date,
                    "start_time": date.start_time,
                    "state": app.result,
                    "paid": app.paid,
                })

                english_grade.append({
                    "date": date.reservation_date,
                    "start_time": date.start_time,
                    "score": app.score,
                    "state": app.result,
                    "confirmed": app.confirmed,
                    "original_certificate": app.original_certificate.url if app.original_certificate else None,
                    "university_certificate": app.university_certificate.url if app.university_certificate else None
                })

        if not appEng.exists():
            if docs_state == "accepted":
                english_date = {
                    "eng": [
                        {
                            "num_tries": 0
                        },
                        {
                            "date": None,
                            "state": None
                        }
                    ]
                }

        return docs_state, english_date, english_grade

    @staticmethod
    def check_english_certf(applicant):
        if isinstance(applicant.english_certf_score, float) and applicant.english_certf_score > 0:
            return True
        return False

    @staticmethod
    def prepare_interview_test_applicant(applicant_id):
        interview_date = None
        interview_grade = None

        try:
            interview = Interview.objects.get(applicant_id=applicant_id)

            interview_date = {
                "date": interview.reservation_id.reservation_date,
                "start_time": interview.reservation_id.start_time,
                "state": interview.result
            }
            interview_grade = interview.result
        except Interview.DoesNotExist:
            pass

        return interview_grade, interview_date
