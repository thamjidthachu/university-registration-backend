import re
import random

from django.conf import settings
from rest_framework import serializers

from registration.models.applicant import Applicant
from registration.models.univStructure import Major


class RegisterSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handled each field that coming as a json.
        - validate each field
        - store the data after validate into database or
        - return validate error if you have an error
    """

    # handle expected errors
    error_msg = {
        'name': {'name': 'Name should contain only alpha',
                 'name_ar': 'الاسم يجب ان يحتوى فقط على حروف ابجدية'},
        'email': {'email': "this email already taken please choose another email",
                  'email_ar': 'هذا البريد الإلكتروني مأخوذ بالفعل الرجاء اختيار بريد إلكتروني آخر'},

        'email_null': {'email': "The email shouldn't be empty",
                       'email_ar': 'يجب الا يكون البريد الالكتروني فارغا'},

        'national_id': {'national_id': "This National ID already taken, please choose another National ID",
                        'national_id_ar': 'رقم الهوية المدخل مستخدم مسبقا .. يرجى التأكد من إدخال رقم الهوية الصحيح'},
        'national_id_null': {'national_id': "the National ID shouldn't be empty",
                             'national_id_ar': 'يجب الا يكون رقم الهوية فارغا'},

        'nationalId_invalid': {'nationalId_invalid': "Invalid National ID",
                               'nationalId_invalid_ar': 'رقم الهوية غير صالح'},
        'school_year': {"school_year": "Error in High school Year! Should be 4 numbers only",
                        "school_year_ar": "خطأ في سنة تخرج الثانوية يجب ادخال 4 أرقام فقط "},
        'marital_status': {'marital_status_en': "Should be select Marital Status!",
                           'marital_status_ar': "يجب اختيار الحالة الاجتماعية"},
        'birth_date_hegry': {'birth_date_hegry': "Invalid birth date format",
                             'birth_date_hegry_ar': "خطأ في تاريخ الميلاد الهجري"},
        'secondary_type': {'error': 'Secondary type not a valid choice', 'error_ar': 'نوع الثانوية ليس صحيح'},
        "eng": {"english_score": "Invalid Entry, Please enter a valid number in english certificate Score",
                "english_score_ar": "إدخال غير صالح ، الرجاء إدخال رقم صحيح في درجة الشهادة الإنجليزية"},
        "eng_score": {"english_score": "Sorry, Score should be positive number",
                      "english_score_ar": "عذرًا ، يجب أن تكون النتيجة رقمًا موجبًا وأكبر من صفر"},
    }

    # Should be added model class
    # fields that need to validate it
    class Meta:
        model = Applicant
        fields = ('first_name', 'middle_name', 'last_name', 'family_name', 'arabic_first_name', 'arabic_middle_name',
                  'arabic_last_name', 'arabic_family_name', 'nationality',
                  'mother_nationality', 'phone', 'home_phone', 'superior_name', 'superior_nationalID',
                  'superior_qualification', 'superior_relation', 'superior_phone', 'emergency_name',
                  'emergency_phone', 'emergency_relation', 'emergency_nationalID', 'emergency_qualification',
                  'qiyas_aptitude', 'qiyas_achievement', 'sat_score', 'previous_university', 'previous_GPA',
                  'health_state', 'health_type', 'employment_state', 'birth_place', 'city', 'building_no', 'street_no',
                  'district', 'postal_code', 'extra_code',
                  'certificate_country', 'education_area', 'high_school_year', 'high_school_name', 'high_school_city',
                  'high_school_GPA', 'max_gpa', 'secondary_type',
                  'first_questionare', 'second_questionare', 'email', 'national_id', 'gender', 'birth_date',
                  'birth_date_hegry', 'apply_semester', 'state_university',
                  'tagseer_institute', 'tagseer_department', 'tagseer_GPA', 'tagseer_year', 'tagseer_number',
                  'tagseer_date', 'equation', 'marital_status', 'employer', 'tagseer_country', 'arabic_speaker',
                  'applicant_type', 'english_certf_score', 'degree',
                  'first_periority', 'second_periority', 'third_periority', 'fourth_periority', 'fifth_periority',
                  'sixth_periority', 'seventh_periority', 'eighth_periority', 'ninth_periority', 'tenth_periority'
                  )

    # this function use for validate the data
    # return data if success validate or return errors if you have an error
    def validate(self, validate_data):

        first_name = validate_data.get('first_name')
        middle_name = validate_data.get('middle_name')
        last_name = validate_data.get('last_name')
        family_name = validate_data.get('family_name')
        arabic_first_name = validate_data.get('arabic_first_name')
        arabic_middle_name = validate_data.get('arabic_middle_name')
        arabic_family_name = validate_data.get('arabic_family_name')
        arabic_last_name = validate_data.get('arabic_last_name')
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

        if email is not None:
            if Applicant.objects.filter(email__iexact=email, apply_semester=settings.CURRENT_SEMESTER).exists():
                raise serializers.ValidationError(self.error_msg['email'])
        else:
            raise serializers.ValidationError(self.error_msg['email_null'])

        if national_id is not None:
            if Applicant.objects.filter(national_id=national_id, apply_semester=settings.CURRENT_SEMESTER).exists():
                raise serializers.ValidationError(self.error_msg['national_id'])
        else:
            raise serializers.ValidationError(self.error_msg['national_id_null'])

        if 'high_school_year' in validate_data and validate_data['high_school_year'] is not None:
            if not isinstance(validate_data['high_school_year'], int):
                raise serializers.ValidationError(self.error_msg['school_year'])

        if 'marital_status' not in validate_data:
            raise serializers.ValidationError(self.error_msg['marital_status'])

        if 'birth_date_hegry' in validate_data:
            date = validate_data.get('birth_date_hegry').split('-')
            if len(date) != 3 or len(date[0]) != 4 or len(date[1]) > 2 or int(date[1]) > 12 or len(date[2]) > 2 or int(
                    date[2]) > 31:
                raise serializers.ValidationError(self.error_msg['birth_date_hegry'])

        if validate_data.get('secondary_type') != 'علمي':
            raise serializers.ValidationError(self.error_msg['secondary_type'])

        if 'english_certf_score' in validate_data:
            if not isinstance(validate_data['english_certf_score'], float):
                raise serializers.ValidationError(self.error_msg['eng'])

            if validate_data['english_certf_score'] < 0:
                raise serializers.ValidationError(self.error_msg['eng_score'])

        return validate_data

    # this function is called after success validation
    # it uses for save data into the database
    def create(self, validated_data):
        if settings.MODE != 'production':
            phone_no = "919847092459"
            land_line = "919847092459"
        else:
            phone_no = validated_data.get('phone')
            if validated_data.get('area_code') and validated_data.get('home_phone'):
                land_line = validated_data.get('area_code') + validated_data.get('home_phone')
            elif validated_data.get('home_phone'):
                land_line = validated_data.get('home_phone')

            else:
                land_line = None

        validated_data['application_no'] = random.randint(20000, 1000000000)
        validated_data['first_name'] = validated_data.get('first_name').upper()
        validated_data['middle_name'] = validated_data.get('middle_name').upper()
        validated_data['last_name'] = validated_data.get('last_name').upper()
        validated_data['family_name'] = validated_data.get('family_name').upper()
        validated_data['full_name'] = (
                validated_data.get('first_name') + " " + validated_data.get('middle_name') + " " +
                validated_data.get('last_name') + " " + validated_data.get('family_name')).upper()
        validated_data['arabic_full_name'] = (
                validated_data.get('arabic_first_name') + " " + validated_data.get('arabic_middle_name') + " " +
                validated_data.get('arabic_last_name') + " " + validated_data.get('arabic_family_name')
        )
        validated_data['email'] = validated_data.get('email').lower()
        validated_data['phone'] = phone_no
        validated_data['home_phone'] = land_line
        validated_data['emergency_name'] = validated_data.get('emergency_name').upper() if validated_data.get(
            'emergency_name') else None
        validated_data['emergency_phone'] = validated_data.get('emergency_phone', None)
        validated_data['apply_semester'] = settings.CURRENT_SEMESTER
        validated_data['major_id'] = Major.objects.get(id=validated_data.get('first_periority'))
        validated_data['english_certf_score'] = validated_data.get('english_certf_score', 0)
        validated_data['employer'] = validated_data.get('employer', None)
        validated_data['init_state'] = 'UR'

        # Remove data has no field in database
        if 'area_code' in validated_data:
            validated_data.pop('area_code')

        app = Applicant(**validated_data)
        app.save()

        return app
