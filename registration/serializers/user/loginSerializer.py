from django.conf import settings
from rest_framework import serializers
from registration.models.applicant import Applicant
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q


class LoginSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handled each field that coming as a json.
        - validate login fields
    """
    email = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    # handle expected errors
    error_msg = {
        "inv_cred": {
            "invalid_cred": "Please Enter a correct Email & Password",
            "invalid_cred_ar": "الرجاء إدخال بريد إلكتروني وكلمة مرور صحيحين"
        },
        "already_exists": {
            "error": "You can\'t login with the account of previous semesters please register again on the current "
                     "semester then login with the new registered account",
            "error_ar": "لا يمكنك تسجيل الدخول بحساب فى الفصل السابق، برجاء التسجيل مرة أخرى وتحديث البيانات وقم "
                        "بالدخول بالحساب الجديد"}
    }

    # Should be added model class
    # fields that need to validate it
    class Meta:
        model = Applicant
        fields = ('email', 'password',)

    def validate(self, validate_data):
        email = validate_data.get("email")
        password = validate_data.get('password')

        applicant = Applicant.objects.filter(Q(email__iexact=email) | Q(national_id__exact=email))

        if applicant.exists():
            applicant = applicant.last()

            if applicant.password is None:
                if applicant.national_id != password:
                    raise serializers.ValidationError(self.error_msg['inv_cred'])

                if applicant.apply_semester != settings.CURRENT_SEMESTER:
                    raise serializers.ValidationError(self.error_msg['already_exists'])

            else:

                if applicant.national_id == password and applicant.password is not None:
                    raise serializers.ValidationError(self.error_msg['inv_cred'])

                if applicant.password is not None and not check_password(password, applicant.password):
                    raise serializers.ValidationError(self.error_msg['inv_cred'])

                if applicant.apply_semester != settings.CURRENT_SEMESTER:
                    raise serializers.ValidationError(self.error_msg['already_exists'])

        else:
            raise serializers.ValidationError(self.error_msg['inv_cred'])

        validate_data['applicant'] = applicant
        return validate_data


class SetPassowrdSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handled each field that coming as a json.
        - set password fields
    """
    password1 = serializers.CharField(max_length=128)
    password2 = serializers.CharField(max_length=128)
    id = serializers.IntegerField()

    error_msg = {
        "password": {"password_matched": "This Password isn't matched!",
                     "password_matched_ar": "كلمة المرور هذه غير مطابقة!"},
        "password_match_national": {"password_match_national": "The password shouldn't match with the national id.!",
                                    "password_match_national_ar": "رقم المرور يجب ألا يطابق رقم الهوية"}
    }

    class Meta:
        model = Applicant
        fields = ('id', 'password1', 'password2',)

    def validate(self, attrs):
        password1 = attrs['password1']
        password2 = attrs['password2']
        app = Applicant.objects.get(id=attrs['id'])

        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError(self.error_msg['password'])

        if str(password1) == str(app.national_id):
            raise serializers.ValidationError(self.error_msg['password_match_national'])

        attrs['applicant'] = app
        return attrs

    def update(self, instance, validated_data):
        password = validated_data['password1']
        password = make_password(password)
        instance.password = password
        instance.save()
        return instance
