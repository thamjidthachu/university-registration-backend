from rest_framework import serializers
from ...models.applicant import Applicant
from django.contrib.auth.hashers import make_password


class ApplicantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ('id', 'phone', 'email',)


class ApplicantProfileUpdateSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    email = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128, required=False)

    class Meta:
        model = Applicant
        fields = ('id', 'email', 'phone', 'password',)

    error_msg = {
        'email': {'email': "Sorry, This email already Taken!", "email_ar": "عذرا هذا البريد الالكترونى تم التسجيل به من قبل"},
        'email_null': {'email': "The email shouldn't be empty", 'email_ar': 'يجب الا يكون البريد الالكتروني فارغا'},
        'phone': {'phone': "Sorry, This phone already Taken!", "phone_ar": "عذرا هذا البريد الالكترونى تم الرقم به من قبل"},
        'phone_null': {'phone': "the phone shouldn't be empty", "phone_ar": "يجب الا يكون رقم الجوال فارغا"},
    }

    def validate(self, attrs):

        applicant = None
        check1 = Applicant.objects.filter(id=attrs['id'], email=attrs['email'])
        check2 = Applicant.objects.filter(id=attrs['id'], phone=attrs['phone'])

        if attrs['email'] is None:
            raise serializers.ValidationError(self.error_msg['email_null'])

        if attrs['phone'] is None:
            raise serializers.ValidationError(self.error_msg['phone_null'])

        if not check1.exists():
            if Applicant.objects.filter(email__iexact=attrs['email']).exists():
                raise serializers.ValidationError(self.error_msg['email'])
        else:
            applicant = check1.first()
        if not check2.exists():
            if Applicant.objects.filter(phone=attrs['phone']).exists():
                raise serializers.ValidationError(self.error_msg['phone'])
        else:
            applicant = check1.first()

        return attrs

    def update(self, instance, validated_data):
        instance.phone = validated_data['phone']
        instance.email = validated_data['email']
        if validated_data['password'] is not None:
            instance.password = make_password(validated_data['password'])
        instance.save()
        return instance
