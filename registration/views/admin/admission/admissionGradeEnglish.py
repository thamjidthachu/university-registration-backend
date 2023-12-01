from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from registration.serializers.admin.admissionSerializer import SetDateSerializer, AdmissionSetEnglishSerializer, AdmissionUpdateEnglishSerializer
from registration.models.evaluation import EnglishTest
from registration.models.applicant import Payment


class AdmissionEnglishGrade(CreateAPIView):

    def post(self, request, *args, **kwargs):

        if "start_time" in self.request.data and 'test_date' in self.request.data and 'date_type' in self.request.data:
            applicant = self.get_applicant_english(self.request.data['applicant_id'])
            if applicant.exists():
                if len(applicant) == 2 and applicant.last().result is not None:
                    return Response({"error": "This applicant has been take the maximum number of tries","error_ar":"لقد تجاوزت الحد الأقصى للمحاولات"},
                                    status=HTTP_400_BAD_REQUEST)
                elif len(applicant) == 1 and applicant.last().result is not None:
                    return Response({"error": "This applicant already set the grade","error_ar":"بالفعل تم وضع الدرجة"},
                                    status=HTTP_400_BAD_REQUEST)
                elif len(applicant) == 2:
                    if not self.check_payment(int(self.request.session['user']['pk'])).exists():
                        return Response({"error": "This applicant isn't paid english fees yet!","error_ar":"عفوا,لم يتم دفع رسوم الإختبار "},
                                        status=HTTP_400_BAD_REQUEST)

                self.request.data['user'] = int(self.request.session['user']['pk'])
                eng = AdmissionUpdateEnglishSerializer(data=self.request.data)
                eng.is_valid(raise_exception=True)
                eng.update(applicant.last(), eng.validated_data)

            else:
                date_data = {
                    "start_time": self.request.data['start_time'],
                    "reservation_date": self.request.data['test_date'],
                    "test_type": self.request.data['date_type'],
                    "capacity": 1,
                    "duration_time": 1,
                    "user": int(self.request.session['user']['pk'])

                }
                date = SetDateSerializer(data=date_data)
                date.is_valid(raise_exception=True)
                date = date.save()
                intr = {
                    "test_type": self.request.data['test_type'],
                    "score": self.request.data['score'],
                    "result": self.request.data['result'],
                    "user": int(self.request.session['user']['pk']),
                    "applicant_id": self.request.data['applicant_id'],
                    "reservation_id": date.id,
                    "test_try": 1,
                }
                reservation = AdmissionSetEnglishSerializer(data=intr)
                reservation.is_valid(raise_exception=True)
                reservation.create(reservation.validated_data)

            return Response({"success": "Successfully added"}, status=HTTP_200_OK)

        return Response({"error": "Invalid passing data","error_ar":"خطأ فى ارسال البيانات"}, status=HTTP_400_BAD_REQUEST)

    def get_applicant_english(self, id):
        return EnglishTest.objects.filter(applicant_id_id=id)

    def check_payment(self, id):
        return Payment.objects.filter(applicant_id_id=id, payment_id__payment_title__exact="ERET", paid=True)