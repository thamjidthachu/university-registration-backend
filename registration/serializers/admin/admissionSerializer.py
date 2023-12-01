import re

from django.conf import settings
from django.utils.timezone import datetime
from rest_framework import serializers

from equations.models.services import Service
from registration.models.evaluation import Absent
from registration.models.sysadmin import Role
from registration.serializers.user.uploadSerializer import handle_error_msg
from registration.system_log.logs import Logs
from ...models.applicant import Applicant, Files, Reservation, Note
from ...models.evaluation import EnglishTest, Interview
from ...models.univStructure import Major, MAJOR_CHOICES
from ...models.user_model import User


class AddUserSerializer(serializers.ModelSerializer):
    error_msg = {
        "full_name": {"full_name": "Full Name should contain only english alpha",
                      "full_name_ar": "الاسم كامل يجب ان يكون حروف انجليزية فقط"},
        "username": {"username": "Username Should be contain only english alpha",
                     "username_ar": "اسم المستخدم يجب ان يكون حروف انجليزية فقط"}
    }

    class Meta:
        model = User
        fields = ('full_name', 'userName', 'gender', 'signature', 'email', 'Phone',)

    def validate(self, attrs):
        pattern_fullname = r'^[a-z A-z ]+$'
        pattern_username = r'^[a-z A-z 0-9 @#._ ]+$'

        if not re.match(pattern_fullname, attrs['full_name']):
            raise serializers.ValidationError(self.error_msg['full_name'])

        if not re.match(pattern_username, attrs['userName']):
            raise serializers.ValidationError(self.error_msg['username'])

        return attrs

    def create(self, validated_data):

        user = User(
            full_name=validated_data.get('full_name'),
            userName=validated_data.get('userName'),
            Phone=validated_data.get('Phone'),
            email=validated_data.get('email'),
            gender=validated_data.get('gender'),
            role=11,

        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class AdmissionAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ("file_name", "url", "status", "rej_reason",)

    error_msg = {
        'limit_size': {"limit_size": "The size of %(filename)s should be less than %(size)s MB ",
                       "limit_size_ar": "حجم فايل %(filename)s يجب ان يكون مساحته اقل من %(size)s ميجا"},
        "image_type": {
            "image_type": "Error in %(field_name)s field! The file upload should be jpeg, jpg, png, pdf only",
            "image_type_ar": "خطأ فى حقل %(field_name)s , الفايل المرفوع يجب ان يكون بصيغة jpeg, jpg, png, pdf فقط"},
        "file_name": {"file_name": "please Upload your %(file_name)s!",
                      "file_name_ar": "برجاء رفع %(file_name)s تبعك !"},
        "status": {"status": "Please select from List!",
                   "status_ar": "برجاء الاختيار من القائمة"},
        "rej_reason": {"rej_reason": "Please enter the message rejection",
                       "rej_reason_ar": "برجاء ادخال سبب الرفض"}

    }
    # set constant Limit size for file
    MAX_SIZE = 5 * 1024 * 1024

    def validate(self, validate_data):
        file = validate_data.get('file_name')
        url = validate_data.get('url')
        if url is None:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['file_name'], {'file_name': str(file).replace("_", " ")}))

        elif url.content_type.split("/")[1] not in ['jpeg', 'jpg', 'png', 'pdf']:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['image_type'], {'file_name': str(file).replace("_", " ")}))

        elif url.size > self.MAX_SIZE:
            raise serializers.ValidationError(
                handle_error_msg(self.error_msg['limit_size'], {'filename': url, "size": "5"}))

        if validate_data.get("rej_reason") is None:
            raise serializers.ValidationError(self.error_msg['rej_reason'])

        return validate_data

    def update(self, instance, validated_data):
        instance.url = validated_data.get("url")
        instance.status = validated_data.get("status")
        instance.rej_reason = validated_data.get("rej_reason")
        instance.user = validated_data.get("user")
        instance.save()
        return instance


class AdmissionUpdateApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("init_state", "condition",)


class FileListSerializer(serializers.ModelSerializer):
    class Meta:
        # many = True
        model = Files
        fields = "__all__"


class MajorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = "__all__"

    def update(self, instance, validated_data, user_id):
        date = datetime.now()
        user = User.objects.get(id=user_id)
        old = {
            "status": True if instance.status == 1 else False,
            "status_m": True if instance.status_m == 1 else False,
        }
        new = {
            "status": True if validated_data.get('status') == 1 else False,
            "status_m": True if validated_data.get('status_m') == 1 else False,
        }
        instance.status_m = validated_data.get('status_m')
        instance.status = validated_data.get('status')
        instance.action_date = date
        instance.user = user
        Logs(user, dict(MAJOR_CHOICES)[instance.name] + " (major modified)", old, new, date)
        instance.save()
        return instance


class DisabilityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = "__all__"


class ApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("full_name", "arabic_full_name", "init_state", "major_id", "id", "national_id", 'registration_date',
                  'contacted', 'contact_result', 'student_id',)


class UnregisteredApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = (
            "full_name", "arabic_full_name", "init_state", "email", "phone", "id", "national_id", 'registration_date',
            'contacted', 'contact_result', 'major_id')


class ReservationDateRetreiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('reservation_date', 'start_time',)


class EnglishRetreiveSerializer(serializers.ModelSerializer):
    reservation_id = ReservationDateRetreiveSerializer()

    class Meta:
        model = EnglishTest
        fields = (
            'reservation_id', 'result', 'score', 'test_type', 'test_try', 'original_certificate',
            'university_certificate', 'confirmed', 'paid',
        )


class InterviewRetreiveSerializer(serializers.ModelSerializer):
    reservation_id = ReservationDateRetreiveSerializer()

    class Meta:
        model = Interview
        fields = ('reservation_id', 'result', 'university_certificate')


# retrieve applicant data from files
class ApplicantPerioritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("first_periority", 'second_periority', 'third_periority', 'fourth_periority', 'fifth_periority',
                  'sixth_periority', 'seventh_periority', 'eighth_periority', 'ninth_periority', 'tenth_periority',)


class ApplicantRetreiveSerializer(serializers.ModelSerializer):
    modified_user = AddUserSerializer()

    class Meta:
        model = Applicant
        fields = ("id", "full_name", "arabic_full_name", "init_state", "major_id", "apply_semester",
                  "applicant_type", "condition", 'contacted', 'high_school_GPA',
                  'qiyas_aptitude', 'qiyas_achievement', 'previous_GPA', "email", "phone", "final_state",
                  'accepted_outside', 'init_state_date', 'notes', 'national_id', 'max_gpa',
                  'high_school_year', 'secondary_type', "student_id", 'university_english_certification',
                  'contact_result', 'english_certf_score', 'english_certf_result',
                  'equation_fees_exempt', 'modified_user')


class ApplicantRejectedRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = (
            "id", "full_name", "arabic_full_name", "english_certf_result", "english_certf_score", "applicant_type",
            "national_id", "major_id", "high_school_GPA", "qiyas_aptitude", "qiyas_achievement", "previous_GPA",
            "email", "phone", "english_certf_confirmation", "university_english_certification", "modify_grader",
            "english_notes", "english_certf_entry_user"
        )


# retrieve files with applicant data info
class FilesApplicantRetreiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ("id", "file_name", "url", "status", "rej_reason", "user",)


class FilesApplicantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ("id", "status", "rej_reason",)

    error_msg = {
        "reject_message": {"reject_message": "Please write the rejection reason message",
                           "reject_message_ar": "برجاء كتابة سبب الرفض"},
    }

    def validate(self, attrs):
        status = attrs['status']
        msg_rej = attrs['rej_reason']

        if status == "RJ":
            if msg_rej is None:
                raise serializers.ValidationError(self.error_msg['reject_message'])

        return attrs

    def update(self, instance, validated_data, user_id):
        old = {}
        new = {}
        status = validated_data['status']
        rej_msg = validated_data['rej_reason']

        if status == "RJ":
            old['reject reason'] = instance.rej_reason
            new['reject reason'] = rej_msg
            instance.rej_reason = rej_msg

        else:
            old['reject reason'] = instance.rej_reason
            new['reject reason'] = None
            instance.rej_reason = None

        old['status'] = instance.status
        new['status'] = status
        instance.status = status
        instance.user = user_id
        date = datetime.now()
        instance.modify_user = date
        Logs(user_id, instance.applicant_id.full_name + " (applicant modified)", old, new, date)
        instance.save()
        return instance


class ApplicantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("condition", "init_state", "init_state_date",)

    error_msg = {
        "condition": {"condition": "Please write the Conditional Acceptance message",
                      "condition_ar": " يرجى كتابة رسالة القبول المشروط "},
    }

    def validate(self, attrs):
        init_state = attrs['init_state']
        condition = attrs['condition']

        if init_state == "CA":
            if condition is None:
                raise serializers.ValidationError(self.error_msg['condition'])
        return attrs

    def update(self, instance, validated_data, user):
        old = {}
        new = {}
        init_state = validated_data['init_state']

        if init_state == "CA":
            new['condition'] = validated_data['condition']
            instance.condition = validated_data['condition']
        else:
            instance.condition = None

        if init_state is None or init_state == "":
            new['init state'] = "UR"
            instance.init_state = "UR"
        else:
            old['init state'] = instance.init_state
            new['init state'] = init_state
            instance.init_state = init_state

        instance.modified_user = user
        date = datetime.now()
        instance.init_state_date = date
        Logs(user, instance.full_name + " (applicant modified)", old, new, date)
        instance.save()

        return instance


class ApplicantContactedSerializer(serializers.ModelSerializer):
    contacted = serializers.IntegerField()

    class Meta:
        model = Applicant
        fields = ('id', 'contacted', 'contact_result')

    error_msg = {
        "contacted_error": {"contacted": "Sorry, Contacted Should be only True or False",
                            "contacted_ar": "عذرًا ، يجب أن تكون جهة الاتصال صواب أو خطأ فقط"}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_result'].required = False

    def validate(self, attrs):
        if attrs['contacted'] not in [True, False]:
            raise serializers.ValidationError(self.error_msg['contacted_error'])

        return attrs

    def update(self, instance, validated_data):
        old = {
            "contacted": True if instance.contacted == 1 else False
        }
        new = {
            "contacted": True if validated_data['contacted'] == 1 else False
        }
        instance.contacted = validated_data['contacted']
        instance.contact_result = validated_data.get('contact_result', instance.contact_result)
        instance.modified_user = self.context['user']
        Logs(self.context['user'], instance.full_name + " (applicant modified)", old, new, datetime.now())
        instance.save()
        return instance


class DateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            "id", "test_type", "gender", "capacity", "count", "reservation_date", "start_time", "duration_time",
            "reserved",
            "online", "faculty")


class SetDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        # fields = (
        #     "test_type", "gender", "capacity", "reservation_date", "start_time", "duration_time", "user",
        #     "online", "faculty ",
        # )
        fields = "__all__"

    error_msg = {
        "date": {"reservation_date": "Please reserve date after the current date!",
                 "reservation_date_ar": "يرجى حجز التاريخ بعد التاريخ الحالي!"},
        "capacity": {"capacity": "Sorry, Capacity should be greater than 0",
                     "capacity_ar": "عذرًا ، يجب أن تكون السعة أكبر من صفر"},
        "capacity_": {"capacity": "Invalid entry number",
                      "capacity_ar": "رقم الإدخال غير صحيح"},
        "dup": {"reservation_date_dup": "Sorry, this date already Taken",
                "reservation_date_dup_ar": "معذرة ، هذا التاريخ تم تسجيله من قبل"},
        "duration": {"duration": "Duration time should be numbers only",
                     "duration_ar": "الوقت المحدد يجب ان يكون ارقام فقط"},

        "duration_": {"duration_number": "Duration time should be grater than 0",
                      "duration_number_ar": "الوقت المحدد يجب ان يكون اكبر من الصفر"},

        "start_time": {"start_time": "This time has passed",
                       "start_time_ar": "الوقت المحدد تم تجاوزه"}

    }

    def validate(self, attrs):
        capacity = attrs['capacity']
        date = attrs['reservation_date']
        if not isinstance(capacity, int):
            raise serializers.ValidationError(self.error_msg['capacity_'])

        if not isinstance(attrs['duration_time'], float):
            raise serializers.ValidationError(self.error_msg['duration'])

        if attrs['duration_time'] <= 0:
            raise serializers.ValidationError(self.error_msg['duration_'])

        if capacity <= 0:
            raise serializers.ValidationError(self.error_msg['capacity'])

        if date < datetime.now().date():
            raise serializers.ValidationError(self.error_msg['date'])

        if attrs['start_time'] <= datetime.now().time() and date == datetime.now().date():
            raise serializers.ValidationError(self.error_msg['start_time'])

        if Reservation.objects.filter(reservation_date=date,
                                      start_time=attrs['start_time'],
                                      test_type=attrs['test_type'],
                                      faculty=attrs['faculty']).exists():
            raise serializers.ValidationError(self.error_msg['dup'])

        return attrs


class UpdateDateSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    id = serializers.IntegerField()

    class Meta:
        model = Reservation
        fields = ("id", "test_type", "capacity", "count",)

    error_msg = {
        "capacity": {"capacity": "Sorry, Capacity should be greater than the number of reserved applicants",
                     "capacity_ar": "عذرًا ، يجب أن تكون السعة أكبر من عدد الطلاب الحاجزين"},
        "capacity_": {"capacity": "Invalid entry number",
                      "capacity_ar": "رقم الإدخال غير صحيح"},

    }

    def validate(self, attrs):
        count = attrs['count']
        capacity = attrs['capacity']

        if not isinstance(capacity, int):
            raise serializers.ValidationError(self.error_msg['capacity_'])

        if count > capacity:
            raise serializers.ValidationError(self.error_msg['capacity'])

        attrs['reservation'] = Reservation.objects.get(id=attrs['id'])

        return attrs

    def update(self, instance, validated_data):

        instance.capacity = validated_data['capacity']
        instance.user = validated_data['user']

        instance.save()

        return instance


class UpdateScoreApplicantSerializer(serializers.ModelSerializer):
    english_certf_score = serializers.CharField(required=False)
    high_school_GPA = serializers.CharField(required=False)
    qiyas_aptitude = serializers.CharField(required=False)
    qiyas_achievement = serializers.CharField(required=False)
    previous_GPA = serializers.CharField(required=False)

    class Meta:
        model = Applicant
        fields = (
            'id', 'english_certf_score', 'high_school_GPA', 'qiyas_aptitude', 'qiyas_achievement', 'previous_GPA',
        )

    error_msg = {
        "number": {"number": "Sorry, Invalid Entry", "number_ar": "خطا فى الادخال"},
    }

    def update(self, instance, validated_data):
        try:
            user = User.objects.get(id=validated_data.get('user'))
        except User.DoesNotExist:
            user = None
        old = {
            "High school GPA": instance.high_school_GPA,
            "Qiyas Aptitude": instance.qiyas_aptitude,
            "Qiyas Achievement": instance.qiyas_achievement,
            "Previous GPA": instance.previous_GPA,
            "English Certificate Score": instance.english_certf_score,
        }
        new = {
            "High school GPA": validated_data.get('high_school_GPA', instance.high_school_GPA),
            "Qiyas Aptitude": validated_data.get('qiyas_aptitude', instance.qiyas_aptitude),
            "Qiyas Achievement": validated_data.get('qiyas_achievement', instance.qiyas_achievement),
            "Previous GPA": validated_data.get('previous_GPA', instance.previous_GPA),
            "English Certificate Score": validated_data.get('english_certf_score', instance.english_certf_score),
        }

        instance.high_school_GPA = validated_data.get('high_school_GPA', instance.high_school_GPA)
        instance.qiyas_aptitude = validated_data.get('qiyas_aptitude', instance.qiyas_aptitude)
        instance.qiyas_achievement = validated_data.get('qiyas_achievement', instance.qiyas_achievement)
        instance.previous_GPA = validated_data.get('previous_GPA', instance.previous_GPA)
        if validated_data.get('english_certf_score'):
            instance.english_certf_result = None
            instance.english_certf_score = validated_data.get('english_certf_score')
        if user:
            Logs(user, instance.full_name + " (applicant modified)", old, new, datetime.now())
        instance.save()

        return instance


class addNotesApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('note',)

    error_msg = {
        "Note": {"Note": "Sorry, Invalid Entry", "Note_ar": "خطأ فى الادخال"},
    }

    # def update(self, instance, attrs):
    #     old = {
    #         "notes": instance.notes,
    #     }
    #     new = {
    #         "notes": attrs['notes']
    #     }
    #     user = User.objects.get(id=attrs['user'])
    #     instance.notes = attrs['notes']
    #     instance.modified_user = user
    #     Logs(user, instance.full_name + " (applicant modified)", old, new, datetime.now())
    #     instance.save()
    #     return instance

    def create(self, validated_data):
        note = Note(
            modified_user=User.objects.get(id=validated_data['user']),
            applicant_name=validated_data['applicant'],
            note=validated_data['note'],
        )
        note.save()


class updateMailApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ('id', 'email',)

    error_msg = {
        "email": {"email": "Sorry, Invalid Email", "email_ar": "خطأ فى الادخال"},
    }

    def update(self, instance, attrs):
        old = {
            "email": instance.email,
        }
        new = {
            "email": attrs['email'],
        }
        user = User.objects.get(id=attrs['user'])
        instance.email = attrs['email']
        Logs(user, instance.full_name + " (applicant modified)", old, new, datetime.now())
        instance.save()
        return instance


class updatePeriorityApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id", "first_periority", 'second_periority', 'third_periority', 'fourth_periority', 'fifth_periority',
                  'sixth_periority', 'seventh_periority', 'eighth_periority', 'ninth_periority', 'tenth_periority',
                  'major_id',)

    error_msg = {
        "periority": {"periority": "Invalid Entry data", "periority_ar": "خطأ فى الادخال"},
    }

    def update(self, instance, attrs):
        user = User.objects.get(id=attrs['user'])
        old = {
            "first periority": instance.first_periority,
            "second periority": instance.second_periority,
            "third periority": instance.third_periority,
            "fourth periority": instance.fourth_periority,
            "fifth periority": instance.fifth_periority,
            "sixth periority": instance.sixth_periority,
            "seventh periority": instance.seventh_periority,
            "eighth periority": instance.eighth_periority,
            "ninth periority": instance.ninth_periority,
            "tenth periority": instance.tenth_periority,
            "current major": dict(MAJOR_CHOICES)[instance.major_id.name],
        }
        new = {
            "first periority": attrs['first_periority'],
            "second periority": attrs['second_periority'],
            "third periority": attrs['third_periority'],
            "fourth periority": attrs['fourth_periority'],
            "fifth periority": attrs['fifth_periority'],
            "sixth periority": attrs['sixth_periority'],
            "seventh periority": attrs['seventh_periority'],
            "eighth periority": attrs['eighth_periority'],
            "ninth periority": attrs['ninth_periority'],
            "tenth periority": attrs['tenth_periority'],
            "current major": dict(MAJOR_CHOICES)[Major.objects.get(id=attrs['first_periority']).name],
        }
        instance.first_periority = attrs['first_periority']
        instance.second_periority = attrs['second_periority']
        instance.third_periority = attrs['third_periority']
        instance.fourth_periority = attrs['fourth_periority']
        instance.fifth_periority = attrs['fifth_periority']
        instance.sixth_periority = attrs['sixth_periority']
        instance.seventh_periority = attrs['seventh_periority']
        instance.eighth_periority = attrs['eighth_periority']
        instance.ninth_periority = attrs['ninth_periority']
        instance.tenth_periority = attrs['tenth_periority']
        instance.major_id = Major.objects.get(id=attrs['first_periority'])
        Logs(user, dict(MAJOR_CHOICES)[instance.major_id.name] + " (major modified)", old, new, datetime.now())

        instance.save()

        return instance


class ApplicantOutSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ('id', 'accepted_outside', 'major_id',)

    def update(self, instance, attrs, user):
        old = {
            "current major": dict(MAJOR_CHOICES)[instance.major_id.name] if instance.major_id is not None else None,
            "accepted outside": instance.accepted_outside,
            "offer": instance.offer,
            "final state": instance.final_state
        }
        new = {
            "current major": dict(MAJOR_CHOICES)[attrs['major_id'].name],
            "accepted outside": attrs['accepted_outside'],
            "offer": "Accepted",
            "final state": "Accepted"
        }
        instance.major_id = attrs['major_id']
        instance.accepted_outside = attrs['accepted_outside']
        instance.offer = "AC"
        instance.init_state = "IA"
        instance.final_state = "A"
        Logs(user, instance.full_name + " (applicant modified)", old, new, datetime.now())
        instance.save()
        return instance


class ApplicantFinalAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id", "full_name", "arabic_full_name", "init_state", "email",
                  "phone", "national_id", 'student_id', 'registration_date', 'major_id', 'final_state_date',)


class getNotesApplicantSerializer(serializers.ModelSerializer):
    modified_user = AddUserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ('modified_user', 'note', 'created')


class AdmissionSetEnglishSerializer(serializers.ModelSerializer):
    test_try = serializers.IntegerField()

    class Meta:
        model = EnglishTest
        fields = "__all__"

    error_msg = {
        "applicantId": {"applicant_id": "You alraedy reserved English Test date!",
                        "applicant_id_ar": "لقد حجزت بالفعل موعد اختبار اللغة الإنجليزية!"},
    }

    def validate(self, attrs):

        applicant = EnglishTest.objects.filter(applicant_id=attrs['applicant_id'].id)

        if applicant.exists() and len(applicant) == 2:
            raise serializers.ValidationError(self.error_msg['applicantId'])

        if len(applicant) == 1:
            attrs['test_try'] = 2

        return attrs

    def create(self, validated_data):
        add = EnglishTest(
            applicant_id=validated_data['applicant_id'],
            reservation_id=validated_data['reservation_id'],
            test_try=validated_data['test_try'],
            user=validated_data['user'],
            test_type=validated_data['test_type'],
            score=validated_data['score'],
            result=validated_data['result']
        )
        reserv = validated_data['reservation_id']
        reserv.count = reserv.count + 1
        reserv.reserved = True
        reserv.save()
        return add.save()


class AdmissionUpdateEnglishSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnglishTest
        fields = ('test_type', 'user', 'score', 'result',)

    def update(self, instance, validated_data):
        # old = {
        #     "test_type": No
        # }
        # new = {}

        instance.user = validated_data['user']
        instance.test_type = validated_data['test_type']
        instance.score = validated_data['score']
        instance.result = validated_data['result']
        instance.save()
        return instance


class AdmissionSetInterviewSerializer(serializers.ModelSerializer):
    '''
            This class for handle the serializer data that coming as a json data
            - should be handle each field that coming as a json.
            - validate each field
            - store the data after validate into database or
            - return validate error if have an error
        '''

    # handle expected errors
    error_msg = {
        'applicantId': {'applicant_id': "You alraedy reserved Interview date!",
                        "applicant_id_ar": "لقد حجزت بالفعل موعد المقابلة!"},
        'capacity': {'capacity': 'This time slot is no longer can be Reserved',
                     "capacity_ar": "لم يعد من الممكن حجز هذه الفترة الزمنية"},
    }

    # Should be add model class
    # fields that need to validate it
    class Meta:
        model = Interview
        fields = "__all__"

    # this function use for validate the data
    # return data if success validate or return errors if have an error
    def validate(self, validate_data):

        applicant = Interview.objects.filter(applicant_id=validate_data['applicant_id'].id)

        if applicant.exists():
            raise serializers.ValidationError(self.error_msg['applicantId'])
        if validate_data['reservation_id'].capacity == 0:
            raise serializers.ValidationError(self.error_msg['reservationId'])

        return validate_data

    # this function is called after success validation
    # it use for save data into the database
    def create(self, validated_data):

        reserved = Interview(
            applicant_id=validated_data.get('applicant_id'),
            reservation_id=validated_data.get('reservation_id'),
            user=validated_data['user'],
            comment=validated_data['comment'],
            english=validated_data['english'],
            fitness=validated_data['fitness'],
            interest=validated_data['interest'],
            outlook=validated_data['outlook'],
            personality=validated_data['personality'],
            result=validated_data['result'],
            knowledge=validated_data['knowledge']
        )
        reserv = validated_data['reservation_id']
        reserv.count = reserv.count + 1
        reserv.reserved = True
        reserv.save()
        reserved.save()
        return reserved


class admissionUpdateInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        exclude = ('reservation_id', 'applicant_id',)

    def update(self, instance, validated_data):
        instance.user = validated_data['user']
        instance.outlook = validated_data['outlook']
        instance.personality = validated_data['personality']
        instance.interest = validated_data['interest']
        instance.knowledge = validated_data['knowledge']
        instance.fitness = validated_data['fitness']
        instance.english = validated_data['english']
        instance.comment = validated_data['comment']
        instance.result = validated_data['result']
        instance.save()
        return instance


class AdmissionListApplicant(serializers.ModelSerializer):
    id = serializers.IntegerField()

    # handle expected errors
    error_msg = {
        'name': {'name': 'Name should contain only alpha',
                 'name_ar': 'الاسم يجب ان يحتوى فقط على حروف ابجدية'},
        'email': {'email': "this email already taken please choose another email",
                  'email_ar': 'هذا البريد الإلكتروني مأخوذ بالفعل الرجاء اختيار بريد إلكتروني آخر'},
        'national_id': {'national_id': "this National ID already taken please choose another National ID",
                        'national_id_ar': 'رقم الهوية مأخوذ بالفعل من فضلك اختر رقم قومي آخر'},
        'nationalId_invalid': {'nationalId_invalid': "Invalid National ID",
                               'nationalId_invalid_ar': 'رقم قومى غير صالح'},
        'school_year': {"school_year": "Error in High school Year! Should be 4 numbers only",
                        "school_year_ar": "خطأ في سنة تخرج الثانوية يجب ادخال 4 أرقام فقط "},
        'marital_status': {'marital_status_en': "Should be select Marital Status!",
                           'marital_status_ar': "يجب اختيار الحالة الاجتماعية"},
        'secondary_type': {'error': 'Secondary type not a valid choice', 'error_ar': 'نوع الثانوية ليس صحيح'},
    }

    class Meta:
        model = Applicant
        exclude = ('password', 'application_no', 'modified_user', 'final_state', 'init_state', 'registration_date',
                   'offer', 'english_grader', 'major_id', 'first_periority', 'second_periority', 'third_periority',
                   'fourth_periority', 'fifth_periority', 'sixth_periority', 'seventh_periority', 'eighth_periority',
                   'ninth_periority', 'tenth_periority', 'notes', 'accepted_outside', 'contacted', 'condition',
                   'init_state_date', 'equation', 'english_certf_score', 'english_certf_result',
                   'modify_grader', 'student_id', 'university_english_certification',)

    def validate(self, validate_data):

        first_name = validate_data.get('first_name')
        middle_name = validate_data.get('middle_name')
        last_name = validate_data.get('last_name')
        family_name = validate_data.get('family_name')
        arabic_first_name = validate_data.get('arabic_first_name')
        arabic_middle_name = validate_data.get('arabic_middle_name')
        arabic_family_name = validate_data.get('arabic_family_name')
        arabic_last_name = validate_data.get('arabic_last_name')
        applicant_type = validate_data.get('applicant_type')
        email = validate_data.get('email')
        national_id = validate_data.get('national_id')

        pattern_name = r'^[a-zA-zأ-ي ]+$'
        arabic_pattern_name = r'^[\u0621-\u064A0-9 ]+$'

        if not re.match(pattern_name, first_name):
            raise serializers.ValidationError(self.error_msg['name'])

        if not re.match(pattern_name, middle_name):
            raise serializers.ValidationError(self.error_msg['name'])

        if not re.match(pattern_name, last_name):
            raise serializers.ValidationError(self.error_msg['name'])

        if not re.match(pattern_name, family_name):
            raise serializers.ValidationError(self.error_msg['name'])

        if not re.match(arabic_pattern_name, arabic_first_name):
            raise serializers.ValidationError(self.error_msg['name'])

        if not re.match(arabic_pattern_name, arabic_middle_name):
            raise serializers.ValidationError(self.error_msg['name'])

        if not re.match(arabic_pattern_name, arabic_last_name):
            raise serializers.ValidationError(self.error_msg['name'])

        if not re.match(arabic_pattern_name, arabic_family_name):
            raise serializers.ValidationError(self.error_msg['name'])

        check_email = Applicant.objects.filter(email__iexact=validate_data['email'], apply_semester=settings.CURRENT_SEMESTER)
        if check_email.exists():
            if check_email.last().id != validate_data['id']:
                raise serializers.ValidationError(self.error_msg['email'])

        check_national = Applicant.objects.filter(national_id=national_id, apply_semester=settings.CURRENT_SEMESTER)
        if check_national.exists():
            if check_national.last().id != validate_data['id']:
                raise serializers.ValidationError(self.error_msg['national_id'])

        if 'high_school_year' in validate_data and validate_data['high_school_year'] is not None:
            if not isinstance(validate_data['high_school_year'], int):
                raise serializers.ValidationError(self.error_msg['school_year'])

        if 'marital_status' not in validate_data:
            raise serializers.ValidationError(self.error_msg['marital_status'])

        if validate_data.get('secondary_type') != 'علمي':
            raise serializers.ValidationError(self.error_msg['secondary_type'])

        # # check the national id if already exists in e-register
        # if check_national_id(national_id):
        #     raise serializers.ValidationError(self.error_msg['national_id'])

        return validate_data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.full_name = validated_data['first_name'] + ' ' + validated_data['middle_name'] + ' ' + validated_data[
            'last_name'] + ' ' + validated_data['family_name']
        instance.arabic_full_name = validated_data['arabic_first_name'] + ' ' + validated_data[
            'arabic_middle_name'] + ' ' + validated_data['arabic_last_name'] + ' ' + validated_data[
                                        'arabic_family_name']

        if 'arabic_speaker' in validated_data:
            instance.arabic_speaker = validated_data['arabic_speaker']

        instance.applicant_type = validated_data['applicant_type']

        instance.save()
        return instance


class ReservationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('reservation_date', 'start_time', 'online')


class applicantAbsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = (
            "full_name", 'email', "arabic_full_name", "init_state", "major_id", "id", "national_id",
            'registration_date')


class AbsentApplicantSerializer(serializers.ModelSerializer):
    applicant_id = applicantAbsentSerializer()
    reservation_id = ReservationDateSerializer()

    class Meta:
        model = Absent
        fields = ("applicant_id", 'reservation_id')


class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

    error_msg = {
        "service": {"error": "Service not found",
                    "error_ar": "لا توجد هذه الخدمة"}
    }

    def validate(self, attrs):
        service = Service.objects.filter(name=attrs['name'])
        if not service.exists():
            raise serializers.ValidationError(self.error_msg['service'])
        return attrs

    def update(self, instance, validated_data, user_id):
        date = datetime.now()
        user = User.objects.get(id=user_id)
        instance.active = validated_data['active']
        instance.action_date = date
        instance.user = user
        instance.save()
        return instance


class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('role',)


class UpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('role',)

    error_msg = {
        "role": {"error": "Role does not exist",
                 "error_ar": "لا توجد هذه الصلاحية"}
    }

    def validate(self, attrs):
        roles = Role.objects.values_list('role', flat=True)
        roles = list(roles)
        if attrs['role'] not in roles:
            raise serializers.ValidationError(self.error_msg['role'])
        return attrs

    def update(self, instance, validated_data):
        instance.role = validated_data['role']
        instance.save()


class ApplicantEquationFees(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ('equation_fees_exempt',)


class UpdateEnglishCertfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ('english_certf_score',)

    error_msg = {
        "score_1": {"score_error": "score must have value",
                    "score_error_ar": "النتيجة يجب ان تحتوى على قيمة ولا تكون فارغة"},

        "score_2": {"score_error": "Score Must be int or float",
                    "score_error_ar": "يجب ان يكون الرقم صحيح او عشري"},

        "score_3": {"score_error": "score must be between 0 to 100",
                    "score_error_ar": "يجب ان يكون الرقم اكبر من صفر واقل من مائة"},
    }

    def validate(self, attrs):
        score = attrs.get('english_certf_score')
        if score is None:
            raise serializers.ValidationError(self.error_msg['score_1'])

        if not (isinstance(score, float) or isinstance(score, int)):
            raise serializers.ValidationError(self.error_msg['score_2'])

        if score < 0.0 or score > 100:
            raise serializers.ValidationError(self.error_msg['score_3'])
        return attrs

    def update(self, instance, validated_data):
        instance.english_certf_score = validated_data.get('english_certf_score')
        instance.save()
        return instance
