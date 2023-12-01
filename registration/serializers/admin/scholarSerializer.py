from rest_framework import serializers
from ...models.sysadmin import UnivPayments
from ...models.applicant import Payment, Applicant
from registration.system_log.logs import Logs
from registration.models.user_model import User
from django.utils.timezone import now


class ScholarFeesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnivPayments
        fields = '__all__'


class ApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = (
            "id", "full_name", "arabic_full_name", "national_id", 'nationality', 'phone', 'superior_phone', 'email',
            'major_id', 'student_id'
        )


class UnivPayListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnivPayments
        fields = ("payment_title", "cost",)


class PaymentListSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantListSerializer()
    payment_id = UnivPayListSerializer()

    class Meta:
        model = Payment
        fields = ("applicant_id", "payment_id", "payment_date", 'amount',)


class ScholarFeesSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnivPayments
        fields = ("payment_title", "cost",)

    error_msg = {
        "cost": {"cost": "Invalid Entry should be number grater than 0!",
                 "cost_ar": "رقم ادخال غير صحيح ! يجب ان يكون رقم و اكبر من صفر"}
    }

    def validate(self, attrs):
        if attrs['cost'] <= 0:
            raise serializers.ValidationError(self.error_msg['cost'])

        return attrs

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user'])
        Logs(user, user.full_name + " (add payment)", {}, {
            "payment title": dict(UnivPayments.PAY_TYPE)[validated_data['payment_title']],
            "cost": validated_data['cost']
        }, now())
        return UnivPayments(
            payment_title=validated_data['payment_title'],
            cost=validated_data['cost'],
            user=user,
            date_modified=now()
        ).save()


class ScholarFeesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnivPayments
        fields = ("cost",)

    error_msg = {
        "cost": {"cost": "Invalid Entry should be number grater than 0!",
                 "cost_ar": "رقم ادخال غير صحيح ! يجب ان يكون رقم و اكبر من صفر"}
    }

    def validate(self, attrs):
        if attrs['cost'] <= 0:
            raise serializers.ValidationError(self.error_msg['cost'])

        return attrs

    def update(self, instance, validated_data):
        instance.cost = validated_data['cost']
        instance.save()
        return instance
