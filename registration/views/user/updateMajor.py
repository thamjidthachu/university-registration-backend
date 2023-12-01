from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from ...serializers.user.uploadSerializer import updateMajorSerializer
from ...models.applicant import Applicant
from registration.models.evaluation import EnglishTest


class UpdateMajor(GenericAPIView):
    serializer_class = updateMajorSerializer

    def put(self, request):
        applicant = Applicant.objects.get(id=int(self.request.session['user']['pk']))
        major_set = updateMajorSerializer(data=self.request.data)

        if not self.check_next_priority(applicant):
            return Response({
                            "priority": "Please be informed that this is your last periority ,"
                                        " you may contact the university admission to add another periority",
                            "priority_ar": " الرجاء العلم هذه اخر رغبة لك ,"
                                           " يمكنك التواصل مع ادارة القبول والتسجيل بالجامعة لاضافة رغبة اخري"},
                            status=HTTP_400_BAD_REQUEST)
        else:
            major_set.update(applicant)
            english_test = EnglishTest.objects.filter(applicant_id=applicant.id).last()
            english_test.result = "S"
            english_test.save()
            return Response({"response": "Major updated succsessfully",
                             "response_ar": "تم تعديل الرغبة بنجاح"}, status=HTTP_200_OK)

    def check_next_priority(self, applicant):

        if applicant.major_id.id == applicant.first_periority and applicant.second_periority is None:
            return False

        elif applicant.major_id.id == applicant.second_periority and applicant.third_periority is None:
            return False

        elif applicant.major_id.id == applicant.third_periority and applicant.fourth_periority is None:
            return False

        elif applicant.major_id.id == applicant.fourth_periority and applicant.fifth_periority is None:
            return False

        elif applicant.major_id.id == applicant.fifth_periority and applicant.sixth_periority is None:
            return False

        elif applicant.major_id.id == applicant.sixth_periority and applicant.seventh_periority is None:
            return False

        elif applicant.major_id.id == applicant.seventh_periority and applicant.eighth_periority is None:
            return False

        elif applicant.major_id.id == applicant.eighth_periority and applicant.ninth_periority is None:
            return False

        elif applicant.major_id.id == applicant.ninth_periority and applicant.tenth_periority is None:
            return False

        return True
