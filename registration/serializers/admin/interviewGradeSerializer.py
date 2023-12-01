from rest_framework import serializers
from registration.models.applicant import Applicant, Reservation, Files
from registration.models.evaluation import Interview
from registration.models.user_model import User
from .admissionSerializer import AddUserSerializer
from ..handleErrorMessage import handle_error_msg
from registration.system_log.logs import Logs
from django.utils.timezone import now


class InterviewGradeSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handle each field that coming as a json.
        - validate each field
        - store the data after validate into database or
        - return validate error if have an error
    """
    applicant_id = serializers.IntegerField()
    gender = serializers.CharField(max_length=10)
    user_id = serializers.IntegerField()
    outlook = serializers.CharField(max_length=100)
    personality = serializers.CharField(max_length=100)
    interest = serializers.CharField(max_length=100)
    knowledge = serializers.CharField(max_length=100)
    fitness = serializers.CharField(max_length=100)
    english = serializers.CharField(max_length=100)
    comment = serializers.CharField(max_length=500)
    result = serializers.CharField(max_length=100)

    # handle expected errors
    error_msg = {
        'applicantId': {'applicant_id': 'Incorrect applicant',
                        "applicant_id_ar": "رقم الطالب غير صحيح"},
        'userId': {'user_id': 'You are not authorized',
                   "user_id_ar": "غير مصرح لك"},
        'outlook': {'outlook': 'Invalid Entry text',
                    "outlook_ar": "نص إدخال غير صالح"},
        'personality': {'personality': 'Invalid Entry text',
                        "personality_ar": "نص إدخال غير صالح"},
        'interest': {'interest': 'Invalid Entry text',
                     "interest_ar": "نص إدخال غير صالح"},
        'knowledge': {'knowledge': 'Invalid Entry text',
                      "knowledge_ar": "نص إدخال غير صالح"},
        'fitness': {'fitness': 'Invalid Entry text',
                    "fitness_ar": "نص إدخال غير صالح"},
        'english': {'english': 'Invalid Entry text',
                    "english_ar": "نص إدخال غير صالح"},
        'comment': {'comment': 'Invalid Entry text',
                    "comment_ar": "نص إدخال غير صالح"},
        'result': {'result': 'Invalid Entry text',
                   "result_ar": "نص إدخال غير صالح"},

    }

    # Should be add model class
    # fields that need to validate it
    class Meta:
        model = Interview
        fields = (
            'applicant_id', 'user_id', 'outlook', 'personality', 'interest', 'knowledge', 'fitness', 'english',
            'comment',
            'result',)

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
        if user.role == 5:
            if ((validate_data.get('outlook') is None) or (validate_data.get('personality') is None)
                    or (validate_data.get('interest') is None) or (validate_data.get('knowledge') is None)
                    or (validate_data.get('fitness') is None) or (validate_data.get('english') is None)
                    or (validate_data.get('comment') is None) or (validate_data.get('result') is None)):
                raise serializers.ValidationError(self.error_msg['outlook'])

        else:

            raise serializers.ValidationError(self.error_msg['userId'])

        return validate_data

    # this function is called after success validation
    # it use for save data into the database
    def update(self, instance, validated_data):

        instance.outlook = validated_data.get('outlook')
        instance.personality = validated_data.get('personality')
        instance.interest = validated_data.get('interest')
        instance.knowledge = validated_data.get('knowledge')
        instance.fitness = validated_data.get('fitness')
        instance.english = validated_data.get('english')
        instance.comment = validated_data.get('comment')
        instance.result = validated_data.get('result')
        instance.user = validated_data.get('user_id')
        instance.save()

        return instance


# retreive all applicant that booking interview

class ApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id", "full_name", "arabic_full_name", "major_id", "national_id", 'gender',)


class ReservationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("reservation_date", "start_time",)


class InterviewListSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantListSerializer()
    reservation_id = ReservationDateSerializer()

    class Meta:
        model = Interview
        fields = ("applicant_id", "result", 'reservation_id',)


class ApplicantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("full_name", "arabic_full_name", "national_id","major_id", "apply_semester", "applicant_type",
                  'high_school_GPA', 'qiyas_aptitude', 'qiyas_achievement', 'previous_GPA',
                  'email', 'phone', 'final_state', 'english_certf_score', 'high_school_year', 'arabic_speaker',)


class InterviewResultSerializer(serializers.ModelSerializer):
    error_msg = {
        "field": {"field": "Error in %(field)s! This field is required!"},
        "update": {"update_fail_en": "This applicant is already reviewed by Dean, So you can't update his data",
                   "update_fail_ar": "تمت مراجعة هذا الطالب من قبل العميد ، لذلك لا يمكنك تحديث بياناته"}
    }

    class Meta:
        model = Interview
        fields = ("id", "outlook", "personality", "interest", "knowledge", "fitness", "english", "comment", "result",)

    def update(self, instance, validated_data, user):
        old = {}
        new = {}
        for field in validated_data:
            old[field.replace("_", " ")] = getattr(instance, field)
            new[field.replace("_", " ")] = validated_data[field]
            setattr(instance, field, validated_data[field])

        instance.user = user
        date = now()
        instance.date_modified = date
        Logs(user, instance.applicant_id.full_name + " (applicant modified)", old, new, date)
        instance.save()

        return instance


class InterviewScoreSerializer(serializers.ModelSerializer):
    error_msg = {
        "field": {"field": "Error in %(field)s! This field is required!"},
        "update": {"update_fail_en": "This applicant is already reviewed by Dean, So you can't update his data",
                   "update_fail_ar": "تمت مراجعة هذا الطالب من قبل العميد ، لذلك لا يمكنك تحديث بياناته"}
    }

    class Meta:
        model = Interview
        fields = ("id", "outlook", "personality", "interest", "knowledge", "fitness", "english", "comment", "result",)

    def update(self, instance, validated_data, user):
        old = {}
        new = {}
        for field in validated_data:
            old[field.replace("_", " ")] = getattr(instance, field)
            new[field.replace("_", " ")] = validated_data[field]
            setattr(instance, field, validated_data[field])
        instance.save()
        return instance


class InterviewSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantProfileSerializer()
    reservation_id = ReservationDateSerializer()
    user = AddUserSerializer()

    # id = InterviewSerializer()

    class Meta:
        model = Interview
        fields = ("id", "applicant_id", "reservation_id", "user", "university_certificate", "outlook",
                  "personality", "interest", "knowledge", "fitness", "english", "comment", "result")
