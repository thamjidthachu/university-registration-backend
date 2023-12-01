from rest_framework import serializers
from ...models.user_model import User
from django.contrib.auth import authenticate


class LoginAdminSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handle each field that coming as a json.
        - validate login fields
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    # handle expected errors
    error_msg = {
        "email": {"email": "Please Enter a correct Email!",
                  "email_ar":"برجاء ادخال ايميل صحيح"},
        "password": {"password": "Please Enter a correct Password",
                     "password_ar":"برجاء ادخال رقم سرى صحيح"},
        "inv_cred": {"invalid_cred": "Please Enter a correct Email & Password",
                     "invalid_cred_ar":"برجاء ادخال بريد الكترونى و رقم سري صحيح"}
    }

    # Should be add model class
    # fields that need to validate it
    class Meta:
        model = User
        fields = ('email', 'password',)

    def validate(self, validate_data):
        email = validate_data.get("email")
        user = User.objects.filter(email__iexact=email)
        if not user.exists():
            raise serializers.ValidationError(self.error_msg['inv_cred'])

        auth = authenticate(**validate_data)
        if auth:
            return user
        else:
            raise serializers.ValidationError(self.error_msg['password'])

        return validate_data
