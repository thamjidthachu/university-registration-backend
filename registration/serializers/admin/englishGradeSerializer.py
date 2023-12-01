from rest_framework import serializers
from registration.models.applicant import Applicant, Reservation, EVAL_CHOICES, Files
from registration.models.evaluation import EnglishTest
from django.utils.timezone import now
from ..handleErrorMessage import handle_error_msg
from registration.system_log.logs import Logs
from registration.serializers.admin.admissionSerializer import AddUserSerializer
from django.utils.timezone import datetime

MEGA_SIZE = 5
MAX_SIZE = MEGA_SIZE * 1024 * 1024


class EnglishGradeSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handled each field that coming as a json.
        - validate each field
        - store the data after validate into database or
        - return validate error if you have an error
    """

    # handle expected errors
    error_msg = {
        'score': {'score': 'Invalid Entry Number',
                  "score_ar": "رقم غير صحيح"},

        'limit_size': {"limit_size": "The size of  should be less than %(size)s MB ",
                       "limit_size_ar": "حجم فايل  يجب ان يكون مساحته اقل من %(size)s ميجا"},
        "image_type": {
            "image_type": "Error ! The uploaded file should be jpeg, jpg, png, pdf only",
            "image_type_ar": "خطأ فى حقل , الفايل المرفوع يجب ان يكون بصيغة jpeg, jpg, png, pdf فقط"}
    }

    # Should be added model class
    # fields that need to validate it
    class Meta:
        model = EnglishTest
        fields = ('applicant_id', 'user_id', 'test_type', 'score', 'result', 'original_certificate', 'notes')

    # this function use for validate the data
    # return data if success validate or return errors if you have an error
    def validate(self, validate_data):
        score = validate_data['score']
        if not isinstance(score, float) or not isinstance(score, int):
            raise serializers.ValidationError(self.error_msg['score'])
        original_certificate = validate_data.get('original_certificate')

        if original_certificate.content_type.split("/")[1] not in ['jpeg', 'jpg', 'png', 'pdf']:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['image_type'], {'file_name': "oxford certificate"}))

        elif original_certificate.size > MAX_SIZE:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['limit_size'],
                                 {'filename': original_certificate, "size": str(MEGA_SIZE)}))

        return validate_data

    # this function is called after success validation
    # it uses for save data into the database
    def update(self, instance, validated_data):

        instance.result = validated_data.get('result')
        instance.user = validated_data.get('user_id')
        instance.score = validated_data.get('score')
        instance.test_type = validated_data.get('test_type')
        instance.original_certificate = validated_data.get('original_certificate')
        instance.save()

        return instance


# retreive all applicant that booked interview

class ApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id", "full_name", "arabic_full_name", "major_id", "national_id", 'gender', 'registration_date',)


class ReservationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("reservation_date", "start_time",)


class EnglishListSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantListSerializer()
    reservation_id = ReservationDateSerializer()

    class Meta:
        model = EnglishTest
        fields = ("applicant_id", "result", "test_try", 'reservation_id', 'confirmed')


class ApplicantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id", "full_name", "arabic_full_name", "major_id", "apply_semester",
                  "applicant_type", 'high_school_GPA', 'qiyas_aptitude', 'qiyas_achievement', 'previous_GPA',
                  'email', 'phone', 'national_id', 'arabic_speaker',)


class EnglishResultSerializer(serializers.ModelSerializer):
    original_certificate = serializers.FileField(required=False)
    score = serializers.FloatField(required=False)
    error_msg = {
        "score": {"score": "Invalid entry number"},
        'limit_size': {"limit_size": "The size of  should be less than %(size)s MB ",
                       "limit_size_ar": "حجم فايل  يجب ان يكون مساحته اقل من %(size)s ميجا"},
        "image_type": {
            "image_type": "Error ! The uploaded file should be jpeg, jpg, png, pdf only",
            "image_type_ar": "خطأ فى حقل , الفايل المرفوع يجب ان يكون بصيغة jpeg, jpg, png, pdf فقط"}
    }

    class Meta:
        model = EnglishTest
        fields = ("score", "test_type", "result", "original_certificate", "notes", "entry_user", "confirmed")

    def validate(self, attrs):
        if 'score' in attrs:
            if not isinstance(attrs['score'], float):
                raise serializers.ValidationError(self.error_msg['score'])

        if 'original_certificate' in attrs:
            original_certificate = attrs['original_certificate']

            if original_certificate.content_type.split("/")[1] not in ['jpeg', 'jpg', 'png', 'pdf']:
                raise serializers.ValidationError(
                    handle_error_msg(self.error_msg['image_type'], {'file_name': "oxford certificate"}))

            elif original_certificate.size > MAX_SIZE:
                raise serializers.ValidationError(
                    handle_error_msg(self.error_msg['limit_size'],
                                     {'filename': original_certificate, "size": str(MEGA_SIZE)}))

        return attrs

    def update(self, instance, validated_data, user):
        old = {}
        new = {}
        for field in validated_data:
            old[field.replace("_", " ")] = getattr(instance, field)
            new[field.replace("_", " ")] = validated_data[field]
            setattr(instance, field, validated_data[field])

        instance.user = user
        Logs(user, instance.applicant_id.full_name + " (applicant modified)", old, new, now())
        instance.save()

        return instance


class EnglishConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnglishTest
        fields = ("confirmed", "university_certificate", "notes")

    def update(self, instance, validated_data):
        instance.university_certificate = validated_data.get('university_certificate')
        instance.notes = validated_data.get('notes')
        if not validated_data.get('confirmed'):
            instance.confirmed = None
            instance.user = None
            instance.entry_user = None
            instance.score = None
            instance.result = None
            instance.modify_user = None
        else:
            instance.confirmed = True
        instance.save()

        return instance


class EnglishSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantProfileSerializer()
    reservation_id = ReservationDateSerializer()
    user = AddUserSerializer()

    class Meta:
        model = EnglishTest
        fields = ("applicant_id", "reservation_id", "score", "result", "test_type", 'test_try',
                  'user', 'original_certificate', 'confirmed', 'university_certificate', 'notes', 'entry_user')


class EnglishCurrentSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantProfileSerializer()

    class Meta:
        model = EnglishTest
        fields = ("applicant_id", "reservation_id", "score", "result", "test_type", 'test_try', 'original_certificate',
                  'confirmed', 'university_certificate', 'notes')


# english certificate uploaded

class EnglishCertificateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ('id', 'full_name', "arabic_full_name", 'major_id', 'english_certf_result', 'national_id', 'gender',
                  'english_certf_confirmation', 'university_english_certification', 'modify_grader', 'english_notes')


class EnglishCertificateApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = (
            'id', 'full_name', "arabic_full_name", 'english_certf_result', 'english_certf_score', 'applicant_type',
            'national_id', 'major_id', 'high_school_GPA', 'qiyas_aptitude', 'qiyas_achievement', 'previous_GPA',
            'email', 'phone', 'english_certf_confirmation', 'university_english_certification', 'modify_grader',
            'english_notes', 'english_certf_entry_user'
        )


class EnglishCertificateResultSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Applicant
        fields = ('id', 'english_certf_result', 'english_certf_score', 'english_grader', 'english_notes',
                  'english_certf_entry_user', 'english_certf_confirmation')

    error_msg = {
        "english_certf": {"english_certf_en": "Sorry! you can't change this applicant after Accepted",
                          "english_certf_ar": "عفوا لايمكنك تعديل هذا الطالب بعد نجاحه"}
    }

    def validate(self, attrs):

        app = Applicant.objects.filter(id=attrs['id'])
        if app.exists():
            if app.last().english_certf_result == 'S' and attrs['english_certf_result'] != 'S':
                raise serializers.ValidationError(self.error_msg['english_certf'])

        return attrs

    def update(self, instance, validated_data):
        old = {
            "english_certificate_result": dict(EVAL_CHOICES)[
                instance.english_certf_result] if instance.english_certf_result is not None else None,
        }
        new = {
            "english_certificate_result": dict(EVAL_CHOICES)[validated_data['english_certf_result']],
        }

        instance.english_certf_result = validated_data['english_certf_result']
        instance.english_notes = validated_data['english_notes']
        instance.english_grader = validated_data['user']
        instance.english_certf_score = validated_data.get('english_certf_score', instance.english_certf_score)
        if validated_data['english_certf_result'] in ['F', 'L', 'U']:
            old["english_certificate_score"] = instance.english_certf_score
            new["english_certificate_score"] = validated_data.get('english_certf_score', 0)
            instance.english_certf_score = validated_data.get('english_certf_score', 0)
            instance.english_certf_confirmation = False
            english_files = Files.objects.filter(applicant_id=instance, file_name__in=['academic_ielts', 'step', 'english_certf', 'tofel'])
            for file in english_files:
                file.file_name = "old_" + file.file_name
                file.save()
            
        Logs(validated_data['user'], instance.full_name + " (applicant modified)", old, new, now())
        instance.modify_grader = datetime.now()
        instance.english_certf_entry_user = validated_data['english_certf_entry_user']
        instance.save()

        return instance


class EnglishCertificateConfirmSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Applicant
        fields = ('id', 'english_certf_result', 'english_certf_score', 'english_grader', 'english_certf_confirmation',
                  'university_english_certification', 'modify_grader', 'english_notes')

    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        if not validated_data.get('english_certf_confirmation'):
            instance.english_certf_confirmation = False
            instance.english_certf_result = None
            instance.english_grader = None
            instance.english_certf_entry_user = None
            instance.modify_grader = None
            instance.english_notes = validated_data.get('english_notes')
            instance.save()
            return instance

        instance.english_certf_confirmation = validated_data['english_certf_confirmation']
        instance.university_english_certification = validated_data['university_english_certification']
        instance.english_notes = validated_data['english_notes']
        instance.english_certf_score = validated_data.get('english_certf_score', instance.english_certf_score)
        instance.save()
        return instance
