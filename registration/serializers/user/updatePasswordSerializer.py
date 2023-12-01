from rest_framework import serializers
from ...models.applicant import Applicant
import re


class UpdatePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     style={'input_type': 'password', 'placeholder': 'Password'}
                                     )

    password1 = serializers.CharField(write_only=True,
                                      required=True,
                                      style={'input_type': 'password', 'placeholder': 'Password'}
                                      )

    id = serializers.IntegerField()

    class Meta:
        model = Applicant
        fields = ("id", 'password', 'password1',)

    error_msg = {
        "password": {"password_matched": "This Password isn't matched!",
                     "password_matched_ar": "كلمة المرور هذه غير مطابقة!"},
        "password_match_national": {"password_match_national": "The password shouldn't match with the national id.!",
                                    "password_match_national_ar": "رقم المرور يجب ألا يطابق رقم الهوية"},
        "password_strength_check": {"password_strength_check_en": "Password must have minimum 8 characters, alphanumeric with at least one uppercase, one lowercase and one special character.",
                     "password_strength_check_ar": "يجب أن تتكون كلمة المرور من 8 أحرف على الأقل، وأبجدية رقمية تحتوي على حرف كبير واحد على الأقل، وحرف صغير واحد، وحرف خاص واحد على الأقل."},
    }

    def validate(self, attrs):
        passowrd = attrs['password']
        passowrd1 = attrs['password1']
        app = Applicant.objects.get(id=attrs['id'])

        if passowrd and passowrd1 and passowrd != passowrd1:
            raise serializers.ValidationError(self.error_msg['password'])

        if passowrd:
            if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})", passowrd):
                raise serializers.ValidationError(self.error_msg['password_strength_check'])

        if str(passowrd) == str(app.national_id):
            raise serializers.ValidationError(self.error_msg['password_match_national'])

        attrs['applicant'] = app
        return attrs

    def update(self, instance, validated_data):
        from django.contrib.auth.hashers import make_password
        password = make_password(validated_data['password'])
        instance.password = password
        instance.save()
        return instance
