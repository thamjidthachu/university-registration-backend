from django.db.models import Q
from rest_framework.response import Response
from ...models.applicant import Applicant
from ...models.evaluation import EnglishTest, Interview
from rest_framework.generics import GenericAPIView
from ...models.applicant import Payment
from ...models.sysadmin import UnivPayments


class statistics(GenericAPIView):
    def get(self, request):
        # reported Numbers

        app_all = Applicant.objects.all().count()
        reg_IA = Applicant.objects.filter(init_state='IA').count()
        reg_CA = Applicant.objects.filter(init_state='CA').count()
        reg_UR = Applicant.objects.filter(init_state='UR').count()
        reg_Cert_Res_S = Applicant.objects.filter(english_certf_result='S').count()
        Eng_S = EnglishTest.objects.filter(result='S').count()
        Eng_S_all = reg_Cert_Res_S + Eng_S
        Eng_P = EnglishTest.objects.filter(result='P').count()
        In_S = Interview.objects.filter(result='S').count()
        App_off_AC = Applicant.objects.filter(offer='AC').count()
        App_Ac = Interview.objects.filter(applicant_id__final_state='A').count()
        App_W = Interview.objects.filter(applicant_id__final_state='W').count()

        # Payments Numbers

        Eng_ = UnivPayments.objects.get(payment_title="ERET")
        Eng_Cost = float(Eng_.cost)
        Paid_ERET_S = Payment.objects.filter(paid=True, payment_id__payment_title="ERET").count()
        Paid_ERET_SAUDI = Payment.objects.filter(paid=True, payment_id__payment_title="ERET",
                                                 applicant_id__nationality="SAUDI").count() * Eng_Cost
        Paid_ERET_out_SAUDI = Payment.objects.filter(~Q(applicant_id__nationality="SAUDI"), paid=True,
                                                     payment_id__payment_title="ERET").count() * Eng_Cost + (
                                          Eng_Cost * .15)

        Reg_ = UnivPayments.objects.get(payment_title="REG")
        Reg_Cost = float(Reg_.cost)
        Paid_REG_S = Payment.objects.filter(paid=True, payment_id__payment_title="REG").count()
        Paid_REG_SAUDI = Payment.objects.filter(paid=True, payment_id__payment_title="REG",
                                                applicant_id__nationality="SAUDI").count() * Reg_Cost
        Paid_REG_out_SAUDI = Payment.objects.filter(~Q(applicant_id__nationality="SAUDI"), paid=True,
                                                    payment_id__payment_title="REG").count() * Reg_Cost + (
                                         Reg_Cost * .15)
        Paid_All = Paid_ERET_SAUDI + Paid_ERET_out_SAUDI + Paid_REG_SAUDI + Paid_REG_out_SAUDI

        return Response({
            "reg_IA": reg_IA,
            "reg_CA": reg_CA,
            "Eng_S_all": Eng_S_all,
            "reg_UR": reg_UR,
            "Eng_P": Eng_P,
            "In_S": In_S,
            "App_off_AC": App_off_AC,
            "App_Ac": App_Ac,
            "App_W": App_W,
            "App_All": app_all,

            "Paid_ERET_S": Paid_ERET_S,
            "Paid_REG_S": Paid_REG_S,
            "Paid_All": Paid_All,

        })
