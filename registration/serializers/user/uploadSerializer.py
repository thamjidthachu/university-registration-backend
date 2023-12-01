from datetime import datetime

from rest_framework import serializers

from registration.models.applicant import Applicant, Files, FINAL_STAT_CHOICES
from registration.models.evaluation import EnglishTest
from ..handleErrorMessage import handle_error_msg
from ...models.univStructure import Major

# set constant Limit size for file
MEGA_SIZE = 5
MAX_SIZE = MEGA_SIZE * 1024 * 1024


class UploadSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handled each field that coming as a json.
        - validate Upload files fields
    """

    english_certf_score = serializers.FloatField(required=False)

    class Meta:
        model = Applicant
        fields = ("gender", 'applicant_type', 'english_certf_score',)

    error_msg = {
        "eng": {"english_score": "Invalid Entry, Please enter a valid number in english certificate Score",
                "english_score_ar": "إدخال غير صالح ، الرجاء إدخال رقم صحيح في درجة الشهادة الإنجليزية"},
        "eng_score": {"english_score": "Sorry, Score should be positive number and greater than 0",
                      "english_score_ar": "عذرًا ، يجب أن تكون النتيجة رقمًا موجبًا وأكبر من صفر"},
    }

    def validate(self, attrs):
        if 'english_certf_score' in attrs:
            if not isinstance(attrs['english_certf_score'], float):
                raise serializers.ValidationError(self.error_msg['eng'])

            if attrs['english_certf_score'] <= 0:
                raise serializers.ValidationError(self.error_msg['eng_score'])

        return attrs

    def update(self, instance, validate_data):
        instance.applicant_type = validate_data.get('applicant_type')
        if 'english_certf_score' in validate_data:
            instance.english_certf_score = validate_data['english_certf_score']
        instance.init_state = "UR"
        instance.save()
        return instance


class UploadFilesSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(max_length=10)

    class Meta:
        model = Files
        fields = ('file_name', 'url', 'gender', 'applicant_id')

    error_msg = {
        'limit_size': {
            'limit_size': 'The size of %(filename)s should be less than %(size)s MB ',
            'limit_size_ar': 'حجم الملف %(filename)s يجب ان يكون مساحته اقل من %(size)s ميجا',
        },
        'image_type': {
            'image_type': 'Error in %(field_name)s field! The file upload should be jpeg, jpg, png, pdf only',
            'image_type_ar': 'خطأ فى حقل %(field_name)s , الملف المرفوع يجب ان يكون بصيغة jpeg, jpg, png, pdf فقط',
        },
        'file_name': {
            'file_name': 'please Upload your %(file_name)s!',
            'file_name_ar': 'برجاء رفع %(file_name)s الخاص بك !',
        },
        'applicantId': {
            'applicantId': 'You already uploaded your files!',
            'applicantId_ar': 'لقد قمت برفع ملفاتك بالفعل',
        },
    }

    def validate(self, attrs):
        file = attrs.get('file_name')
        url = attrs.get('url')

        applicant = Files.objects.filter(applicant_id=attrs['applicant_id'], file_name__exact=attrs['file_name'])
        if applicant.exists():
            raise serializers.ValidationError(self.error_msg['applicantId'])

        if file == 'photo':
            if attrs['gender'] == 'M':
                if url is None:
                    error_msg = self.error_msg['file_name']
                    raise serializers.ValidationError(
                        error_msg['file_name'] % {'file_name': str(file).replace("_", " ")})
        else:
            if url is None:
                error_msg = self.error_msg['file_name']
                raise serializers.ValidationError(error_msg['file_name'] % {'file_name': str(file).replace("_", " ")})

        if url.content_type.split("/")[1] not in ['jpeg', 'jpg', 'png', 'pdf']:
            error_msg = self.error_msg['image_type']
            raise serializers.ValidationError(error_msg['image_type'] % {'field_name': str(file).replace("_", " ")})

        elif url.size > MAX_SIZE:
            error_msg = self.error_msg['limit_size']
            raise serializers.ValidationError(error_msg['limit_size'] % {'filename': url, 'size': str(MEGA_SIZE)})

        return attrs

    def create(self, validated_data):
        return Files(
            applicant_id=validated_data['applicant_id'],
            file_name=validated_data['file_name'],
            url=validated_data['url'],
        ).save()


class RegisterUploadFilesSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(max_length=10)

    class Meta:
        model = Files
        fields = ('file_name', 'url', 'gender', 'applicant_id')

    error_msg = {
        'limit_size': {
            'limit_size': 'The size of %(filename)s should be less than %(size)s MB ',
            'limit_size_ar': 'حجم الملف %(filename)s يجب ان يكون مساحته اقل من %(size)s ميجا',
        },
        'image_type': {
            'image_type': 'Error in %(field_name)s field! The file upload should be jpeg, jpg, png, pdf only',
            'image_type_ar': 'خطأ فى حقل %(field_name)s , الملف المرفوع يجب ان يكون بصيغة jpeg, jpg, png, pdf فقط',
        },
        'file_name': {
            'file_name': 'please Upload your %(file_name)s!',
            'file_name_ar': 'برجاء رفع %(file_name)s الخاص بك !',
        },
        'applicantId': {
            'applicantId': 'You already uploaded your files!',
            'applicantId_ar': 'لقد قمت برفع ملفاتك بالفعل',
        },
    }

    def validate(self, attrs):
        file = attrs.get('file_name')
        url = attrs.get('url')

        applicant = Files.objects.filter(applicant_id=attrs['applicant_id'], file_name__exact=attrs['file_name'])
        if applicant.exists():
            raise serializers.ValidationError(self.error_msg['applicantId'])

        if file == 'photo':
            if attrs['gender'] == 'M':
                if url is None:
                    error_msg = self.error_msg['file_name']
                    raise serializers.ValidationError(
                        error_msg['file_name'] % {'file_name': str(file).replace("_", " ")})
        else:
            if url is None:
                error_msg = self.error_msg['file_name']
                raise serializers.ValidationError(error_msg['file_name'] % {'file_name': str(file).replace("_", " ")})

        if url.content_type.split("/")[1] not in ['jpeg', 'jpg', 'png', 'pdf']:
            error_msg = self.error_msg['image_type']
            raise serializers.ValidationError(error_msg['image_type'] % {'field_name': str(file).replace("_", " ")})

        elif url.size > MAX_SIZE:
            error_msg = self.error_msg['limit_size']
            raise serializers.ValidationError(error_msg['limit_size'] % {'filename': url, 'size': str(MEGA_SIZE)})

        return attrs

    def create(self, validated_data):
        return Files(
            applicant_id=validated_data['applicant_id'],
            file_name=validated_data['file_name'],
            url=validated_data['url'],
        ).save()


class AdmissionFileUploadSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(max_length=10)

    class Meta:
        model = Files
        fields = ('file_name', 'url', 'gender', 'applicant_id')

    error_msg = {
        'limit_size': {
            'limit_size': 'The size of %(filename)s should be less than %(size)s MB ',
            'limit_size_ar': 'حجم الملف %(filename)s يجب ان يكون مساحته اقل من %(size)s ميجا',
        },
        'image_type': {
            'image_type': 'Error in %(field_name)s field! The file upload should be jpeg, jpg, png, pdf only',
            'image_type_ar': 'خطأ فى حقل %(field_name)s , الملف المرفوع يجب ان يكون بصيغة jpeg, jpg, png, pdf فقط',
        },
        'file_name': {
            'file_name': 'please Upload your %(file_name)s!',
            'file_name_ar': 'برجاء رفع %(file_name)s الخاص بك !',
        },
        'applicantId': {
            'applicantId': 'You already uploaded your files!',
            'applicantId_ar': 'لقد قمت برفع ملفاتك بالفعل',
        },
    }

    def validate(self, attrs):
        file = attrs.get('file_name')
        url = attrs.get('url')

        applicant = Files.objects.filter(applicant_id=attrs['applicant_id'], file_name__exact=attrs['file_name'])
        if applicant.exists():
            raise serializers.ValidationError(self.error_msg['applicantId'])

        # if file == 'photo':
        #     if attrs['gender'] == 'M':
        #         if url is None:
        #             error_msg = self.error_msg['file_name']
        #             raise serializers.ValidationError(
        #                 error_msg['file_name'] % {'file_name': str(file).replace("_", " ")})
        # else:
        if url is None:
            error_msg = self.error_msg['file_name']
            raise serializers.ValidationError(error_msg['file_name'] % {'file_name': str(file).replace("_", " ")})

        if url.content_type.split("/")[1] not in ['jpeg', 'jpg', 'png', 'pdf']:
            error_msg = self.error_msg['image_type']
            raise serializers.ValidationError(error_msg['image_type'] % {'field_name': str(file).replace("_", " ")})

        elif url.size > MAX_SIZE:
            error_msg = self.error_msg['limit_size']
            raise serializers.ValidationError(error_msg['limit_size'] % {'filename': url, 'size': str(MEGA_SIZE)})

        return attrs

    def create(self, validated_data):
        return Files(
            applicant_id=validated_data['applicant_id'],
            file_name=validated_data['file_name'],
            url=validated_data['url'],
            # status='A'
        ).save()


class UploadOtherFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ("file_name", 'url', "applicant_id")

    error_msg = {
        "url": {
            "url_error": "url Can't be empty!",
            "url_error_ar": "الملف لا يمكن ان يكون فارغ"
        },
    }

    def validate(self, attrs):
        url = attrs.get('url')
        if not url:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['url'], params=None), )

        return attrs

    def create(self, validated_data):
        return Files(
            file_name=validated_data['file_name'],
            applicant_id=validated_data['applicant_id'],
            url=validated_data['url'],
            modify_user=datetime.now(),
            status='A'
        ).save()


class admissionUploadEnglishFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ("file_name", "url", "applicant_id")

    error_msg = {
        "url": {
            "url_error": "url Can't be empty!",
            "url_error_ar": "الملف لا يمكن ان يكون فارغ"
        },

        "eng": {
            "reservation_found": "Applicant Already Reserved English Test",
            "reservation_found_found_ar": "لقد قام الطالب بحجز إختبار اللغة الإنجليزية"
        },

        "eng_2": {
            "certification_found": "Applicant Already Upload English Certification ",
            "eng_found_ar": "لقد قام الطالب برفع شهادة اللغة الإنجليزية مسبقاً"
        },
    }

    def validate(self, attrs):
        url = attrs.get('url')
        app_id = attrs.get('id')
        # file = attrs.get('file_name')

        if not url:
            raise serializers.ValidationError(handle_error_msg(self.error_msg['url']))

        applicant = EnglishTest.objects.filter(applicant_id=app_id)

        if applicant.exists():
            raise serializers.ValidationError(handle_error_msg(self.error_msg['eng']))

        file = Files.objects.filter(file_name='english_certf', applicant_id=app_id)

        if file.exists():
            raise serializers.ValidationError(handle_error_msg(self.error_msg['eng_2']))

        return attrs

    def create(self, validated_data):
        return Files(
            file_name=validated_data['file_name'],
            applicant_id=validated_data['applicant_id'],
            url=validated_data['url'],
            modify_user=datetime.now(),
            status='A'
        ).save()


class UpdateOtherFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ('url', "user", "file_name")

    error_msg = {
        "url": {"url_error": "url Can't be empty!",
                "url_error_ar": "الملف لا يمكن ان يكون فارغ"},
    }

    def validate(self, attrs):
        url = attrs.get('url')
        if not url:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['url']))

        return attrs

    def update(self, instance, validated_data):
        instance.url = validated_data.get('url')
        instance.user = validated_data.get('user')
        instance.modify_user = datetime.now()
        instance.status = 'A'
        instance.save()
        return instance


class UpdateEnglishFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ('url', "user", "file_name", "applicant_id", "user")

    error_msg = {
        "url": {"url_error": "url Can't be empty!",
                "url_error_ar": "الملف لا يمكن ان يكون فارغ"},
    }

    def validate(self, attrs):
        url = attrs.get('url')
        if not url:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['url']))

        return attrs


    def create(self, validated_data):
        return Files(
            file_name=validated_data['file_name'],
            applicant_id=validated_data['applicant_id'],
            url=validated_data['url'],
            modify_user=datetime.now(),
            user=validated_data.get('user'),
            status='A'
        ).save()


class ReUploadSerializer(serializers.ModelSerializer):
    error_msg = {
        'limit_size': {"limit_size": "The size of %(filename)s should be less than %(size)s MB ",
                       "limit_size_ar": "حجم فايل %(filename)s يجب ان يكون مساحته اقل من %(size)s ميجا"},
        "image_type": {
            "image_type": "Error in %(field_name)s field! The file upload should be jpeg, jpg, png, pdf only",
            "image_type_ar": "خطأ فى حقل %(field_name)s , الفايل المرفوع يجب ان يكون بصيغة jpeg, jpg, png, pdf فقط"},
        "file_name": {"file_name": "please Upload your %(file_name)s!",
                      "file_name_ar": "برجاء رفع %(file_name)s الخاص بك !"},

    }

    class Meta:
        model = Files
        fields = ('file_name', 'url', 'user',)

    def validate(self, validate_data):
        file = validate_data.get('file_name')
        url = validate_data.get('url')
        if url is None:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['file_name'], {'file_name': str(file).replace("_", " ")}))

        # to check the extension of file
        elif url.content_type.split("/")[1] not in ['jpeg', 'jpg', 'png', 'pdf']:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['image_type'], {'file_name': str(file).replace("_", " ")}))

        elif url.size > MAX_SIZE:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['limit_size'], {'filename': url, "size": str(MEGA_SIZE)}))

        return validate_data

    def update(self, instance, validated_data):
        instance.url = validated_data.get('url')
        instance.status = None
        instance.rej_reason = None
        instance.save()
        return instance


class FileSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(max_length=50)
    url = serializers.FileField()
    status = serializers.ChoiceField(FINAL_STAT_CHOICES)
    rej_reason = serializers.CharField(max_length=1000)

    class Meta:
        model = Files
        fields = ('file_name', 'url', 'status', 'rej_reason',)


class EnglishCertificateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ('file_name', 'url',)


class PerioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ('first_periority', 'second_periority', 'third_periority', 'fourth_periority', 'fifth_periority',
                  'sixth_periority', 'seventh_periority', 'eighth_periority', 'ninth_periority', 'tenth_periority')

    def update(self, instance, validated_data):
        instance.first_periority = validated_data.get('first_periority')
        instance.second_periority = validated_data.get('second_periority')
        instance.third_periority = validated_data.get('third_periority')
        instance.fourth_periority = validated_data.get('fourth_periority')
        instance.fifth_periority = validated_data.get('fifth_periority')
        instance.sixth_periority = validated_data.get('sixth_periority')
        instance.seventh_periority = validated_data.get('seventh_periority')
        instance.eighth_periority = validated_data.get('eighth_periority')
        instance.ninth_periority = validated_data.get('ninth_periority')
        instance.tenth_periority = validated_data.get('tenth_periority')
        instance.major_id = Major.objects.get(id=validated_data.get('first_periority'))

        instance.save()

        return instance


class updateMajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id",)

    def validate(self, request_data):

        return request_data

    def update(self, instance):

        if instance.major_id.id == instance.first_periority and instance.second_periority is not None:
            instance.major_id = Major.objects.get(id=instance.second_periority)

        elif instance.major_id.id == instance.second_periority and instance.third_periority is not None:
            instance.major_id = Major.objects.get(id=instance.third_periority)

        elif instance.major_id.id == instance.third_periority and instance.fourth_periority is not None:
            instance.major_id = Major.objects.get(id=instance.fourth_periority)

        elif instance.major_id.id == instance.fourth_periority and instance.fifth_periority is not None:
            instance.major_id = Major.objects.get(id=instance.fifth_periority)

        elif instance.major_id.id == instance.fifth_periority and instance.sixth_periority is not None:
            instance.major_id = Major.objects.get(id=instance.sixth_periority)

        elif instance.major_id.id == instance.sixth_periority and instance.seventh_periority is not None:
            instance.major_id = Major.objects.get(id=instance.seventh_periority)

        elif instance.major_id.id == instance.seventh_periority and instance.eighth_periority is not None:
            instance.major_id = Major.objects.get(id=instance.eighth_periority)

        elif instance.major_id.id == instance.eighth_periority and instance.ninth_periority is not None:
            instance.major_id = Major.objects.get(id=instance.ninth_periority)

        elif instance.major_id.id == instance.ninth_periority and instance.tenth_periority is not None:
            instance.major_id = Major.objects.get(id=instance.tenth_periority)

        instance.save()
        return instance
