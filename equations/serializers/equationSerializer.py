from rest_framework import serializers
from equations.models.equations import Equation
from equations.serializers.equivilantCoursesSerializer import ListEquivilantCoursesSerializer
from registration.serializers.admin.deanEvalSerializer import ApplicantProfileSerializer
from registration.serializers.admin.interviewGradeSerializer import InterviewResultSerializer
from registration.serializers.admin.englishGradeSerializer import EnglishResultSerializer
from registration.models.evaluation import EnglishTest, Interview
from registration.serializers.admin.admissionSerializer import FileListSerializer
from registration.models.applicant import Files
from django.utils.timezone import now
from registration.models.user_model import User


class ListEquationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equation
        exclude = ('user',)

    def to_representation(self, data):
        query = super(ListEquationsSerializer, self).to_representation(data)
        query['equation_courses'] = ListEquivilantCoursesSerializer(data.equation_courses, many=True).data
        query['applicant'] = ApplicantProfileSerializer(data.applicant).data
        query['interview_status'] = InterviewResultSerializer(
            Interview.objects.filter(applicant_id=data.applicant.id).last()).data
        query['english_status'] = EnglishResultSerializer(
            EnglishTest.objects.filter(applicant_id=data.applicant.id).last()).data
        query['transcript'] = FileListSerializer(
            Files.objects.filter(applicant_id=data.applicant.id, file_name='transcript').last()).data
        return query


class CreateEquationSerializer(serializers.ModelSerializer):
    error_msg = {
        "unauthorized": {"error": "You Can't create Equation request.",
                         "error_ar": "لا يمكنك ارسال طلب معادلة."},

        "exist": {"error": "You already have Equation request.",
                  "error_ar": "لديك طلب معادلة بالفعل."},

        "final_state": {"error": "You are not accepted yet to send equation request.",
                        "error_ar": "لم تحصل على قبول نهائي لتقدم طلب معادلة."},
    }

    class Meta:
        model = Equation
        exclude = ('applicant',)

    def validate(self, attrs):
        # if attrs['applicant'].modified_user.role != 1:
        #     raise serializers.ValidationError(self.error_msg['unauthorized'])

        # if attrs['applicant'].final_state != 'A':
        #     raise serializers.ValidationError(self.error_msg['final_state'])

        # if Equation.objects.filter(applicant = attrs['applicant']).exists():
        #     raise serializers.ValidationError(self.error_msg['exist'])

        return attrs


class EditEquationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equation
        fields = '__all__'


class DeanEditEquationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equation
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data['final_state'] == 'NM':
            instance.init_state = 'NM'
            instance.head_of_department_state = None
            instance.final_state = None

        elif validated_data['final_state'] == 'AC':
            instance.final_state = validated_data['final_state']
            instance.confirmed = True
            instance.confirmed_date = now()

        else:
            instance.final_state = validated_data['final_state']
        instance.comment = validated_data.get('comment')
        instance.equation_file = validated_data.get('equation_file')
        instance.final_state_date = now()
        instance.save()

        return instance


class HeadOfDeptEquationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equation
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data['head_of_department_state'] == 'NM':
            instance.init_state = 'NM'
            instance.head_of_department_state = None
            instance.final_state = None
        else:
            instance.head_of_department_state = validated_data['head_of_department_state']
        instance.comment = validated_data.get('comment')
        instance.save()

        return instance


class EquationFileSerializer(serializers.ModelSerializer):
    error_msg = {
        'error': {
            'error': 'Can\'t create a file for this equation',
            'error_ar': 'لا يمكن إنشاء ملف لهذه المعادلة',
        },
        'unauthorized': {
            'error': 'Error updating the equation',
            'error_ar': 'خطأ في تعديل المعادلة',
        },
        'file_required': {
            'error': 'File required',
            'error_ar': 'الملف مطلوب',
        }
    }

    class Meta:
        model = Equation
        fields = ('equation_file',)
        extra_kwargs = {
            'equation_file': {
                'required': True
            }
        }

    def validate(self, attrs):
        if User.objects.get(pk=self.context['user']['pk']).role != 6:
            raise serializers.ValidationError(self.error_msg['unauthorized'])
        return attrs

    def update(self, instance, validated_data):
        if not instance.final_state:
            raise serializers.ValidationError(self.error_msg['error'])
        return super().update(instance, validated_data)
