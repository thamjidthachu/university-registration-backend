from rest_framework import serializers
from registration.models.applicant import Applicant, Files, FINAL_STAT_CHOICES
from registration.models.univStructure import MAJOR_CHOICES, Major
from registration.models.evaluation import Interview, EnglishTest
from registration.models.user_model import User
from registration.system_log.logs import Logs
from django.utils.timezone import now
from django.utils.timezone import datetime
from .admissionSerializer import AddUserSerializer


class DeanEvalSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handle each field that coming as a json.
        - validate each field
        - store the data after validate into database or
        - return validate error if have an error
    """
    applicant_id = serializers.IntegerField()
    major = serializers.CharField(max_length=20)
    final_state = serializers.CharField(max_length=100)

    # handle expected errors
    error_msg = {
        'applicantId': {'applicant_id': 'Incorrect applicant',
                        "applicant_id_ar": "رقم الطالب غير صحيح"},
        'userId': {'user_id': 'You are not authorized',
                   "user_id_ar": "غير مصرح لك"},
        'major': {'major': 'invalid Major',
                  'major_ar': 'تخصص غير صحيح'},
        'finalResult': {'final_state': 'Invalid Entry text',
                        "final_state_ar": "نص إدخال غير صالح"},

    }

    # Should be add model class
    # fields that need to validate it
    class Meta:
        model = Applicant
        fields = ('applicant_id', 'final_state', 'major', 'userId',)

    # this function use for validate the data
    # return data if success validate or return errors if have an error
    def validate(self, validate_data):

        applicant_id = validate_data.get('applicant_id')
        if applicant_id is None or isinstance(applicant_id, int):
            raise serializers.ValidationError(self.error_msg['applicantId'])

        user_id = validate_data.get('user_id')
        if user_id is None or isinstance(user_id, int):
            raise serializers.ValidationError(self.error_msg['userId'])

        user = User.objects.get(pk=user_id)

        if user.role == 7:
            if validate_data.get('final_state') not in ['A', 'RJ', 'W', 'RJM']:
                raise serializers.ValidationError(self.error_msg['final_state'])

        else:
            raise serializers.ValidationError(self.error_msg['userId'])

        return validate_data

    # this function is called after success validation
    # it use for save data into the database
    def update(self, instance, validated_data):

        instance.final_state = validated_data.get('final_state')
        instance.final_state_date = datetime.now()
        instance.save()

        return instance


class DeanEvalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = "__all__"


# retrieve applicant with specific major
class ApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id", "full_name", "arabic_full_name", "final_state", "national_id", 'gender',)


class InterviewRetrieveSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantListSerializer()

    class Meta:
        model = Interview
        fields = ("applicant_id",)


# update final data

class ApplicantProfileSerializer(serializers.ModelSerializer):
    modified_user = AddUserSerializer()

    class Meta:
        model = Applicant
        fields = ("id", "full_name", "arabic_full_name", "init_state", "final_state",
                  "gender", "apply_semester", "applicant_type",
                  "condition", "offer", "major_id", "tenth_periority",
                  "english_certf_result", "english_certf_score",
                  "contacted", 'high_school_GPA', 'qiyas_aptitude',
                  'qiyas_achievement', 'sat_score', 'previous_GPA', 'email',
                  'phone', 'high_graduation_year', 'national_id', 'previous_university', 'student_id', 'arabic_speaker',
                  'tagseer_department', 'tagseer_institute', 'modified_user')

    def update(self, instance, validated_data):
        instance.final_state = validated_data.get('final_state')
        instance.final_state_date = datetime.now()
        instance.save()
        return instance


class ApplicantFinalUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Applicant
        fields = ("id", "modified_user", "final_state",)

    error_msg = {
        "final_state": {"final_state": "Can't be changing the final state of this Applicant.",
                        "final_state_ar": "لا يمكن تغيير الحالة النهائية لهذاالطالب."}
    }

    def update(self, instance, validated_data):
        old = {
            "final state": dict(FINAL_STAT_CHOICES)[instance.final_state] if instance.final_state is not None else None,
            "major": dict(MAJOR_CHOICES)[instance.major_id.name]
        }
        new = {}
        if validated_data.get('final_state') == 'RJM':

            if instance.major_id.id == instance.first_periority and instance.second_periority is not None:
                instance.major_id = Major.objects.get(id=instance.second_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]

            elif instance.major_id.id == instance.second_periority and instance.third_periority is not None:
                instance.major_id = Major.objects.get(id=instance.third_periority)
                instance.final_state = None
                new['major'] = instance.major_id
            elif instance.major_id.id == instance.third_periority and instance.fourth_periority is not None:
                instance.major_id = Major.objects.get(id=instance.fourth_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]

            elif instance.major_id.id == instance.fourth_periority and instance.fifth_periority is not None:
                instance.major_id = Major.objects.get(id=instance.fifth_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]
            elif instance.major_id.id == instance.fifth_periority and instance.sixth_periority is not None:
                instance.major_id = Major.objects.get(id=instance.sixth_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]

            elif instance.major_id.id == instance.sixth_periority and instance.seventh_periority is not None:
                instance.major_id = Major.objects.get(id=instance.seventh_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]

            elif instance.major_id.id == instance.seventh_periority and instance.eighth_periority is not None:
                instance.major_id = Major.objects.get(id=instance.eighth_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]

            elif instance.major_id.id == instance.eighth_periority and instance.ninth_periority is not None:
                instance.major_id = Major.objects.get(id=instance.ninth_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]

            elif instance.major_id.id == instance.ninth_periority and instance.tenth_periority is not None:
                instance.major_id = Major.objects.get(id=instance.tenth_periority)
                instance.final_state = None
                new['major'] = dict(MAJOR_CHOICES)[instance.major_id.name]

            else:
                new['final state'] = dict(FINAL_STAT_CHOICES)['RJ']
                new['major'] = None
                instance.final_state = 'RJ'

        else:
            instance.final_state = validated_data.get('final_state')
            new['final state'] = dict(FINAL_STAT_CHOICES)[validated_data.get('final_state')]
            new['major'] = None

        Logs(validated_data['user'], instance.full_name + " (applicant modified)", old, new, now())

        if validated_data.get('final_state') in ['W', 'RJ', 'RJM']:
            instance.offer = None
        instance.final_state_date = datetime.now()
        instance.modified_user = validated_data['user']
        instance.save()
        intr = validated_data['interview']

        if validated_data['final_state'] in ['W', 'RJM']:
            intr.university_certificate = None
            intr.save()

        return instance


class FilesListSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ("file_name", "status", "rej_reason", "url",)


class InterviewListSerializer(serializers.ModelSerializer):
    user = AddUserSerializer()

    class Meta:
        model = Interview
        fields = ("outlook", "personality", "interest",
                  "knowledge", "fitness", "english", "comment", "result", "university_certificate", 'user')


class EnglishListSerializer(serializers.ModelSerializer):
    user = AddUserSerializer()

    class Meta:
        model = EnglishTest
        fields = ("test_type", "score", "test_try", 'result', 'user',)


class InterviewUpdateCertifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ('university_certificate',)

    def update(self, instance, validated_data):
        instance.university_certificate = validated_data['university_certificate']
        instance.save()
        return instance
