from rest_framework.response import Response
from rest_framework.views import APIView

from email_handling.views.body_mails import studentEquationCreatedMail
from equations.models.equations import Equation
from registration.models.applicant import Applicant
from registration.tasks import send_email


class StudentEquationView(APIView):

    def post(self, request):
        applicant = self.get_applicant(int(self.request.data['applicant_id']))
        equation_obj = Equation.objects.filter(applicant=applicant.id)
        if equation_obj.exists():
            return Response({"error": "You already have Equation request.",
                             "error_ar": "لديك طلب معادلة بالفعل."}, status=401)
        else:
            Equation.objects.create(applicant=applicant)
            # Send Email
            body = studentEquationCreatedMail()
            send_email.delay(request.headers.get("origin"), applicant.first_name, applicant.email,
                             english=body['english'], arabic=body['arabic'],
                             subject='Al Maarefa University KSA Equation Request'
                             )

        return Response({"success": "Equation Request Sent Successfully.",
                         "success_ar": "تم اضافة طلب المعادلة بنجاح."})

    def get_applicant(self, student):
        return Applicant.objects.get(id=student)

    def get_equation(self, id):
        return Equation.objects.get(id=id)
