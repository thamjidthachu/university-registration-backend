from rest_framework import serializers
from ...models.sysadmin import UnivPayments
from ...models.applicant import Payment
from django.utils.timezone import datetime
from registration.serializers.admin.admissionSerializer import AddUserSerializer, ApplicantListSerializer


class PaySerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=20)

    class Meta:
        model = Payment
        fields = ("applicant_id", "checkout_id", "amount", 'type', 'entity_id', 'by_cash')

    def validate(self, attrs):
        app = Payment.objects.filter(payment_id__payment_title=attrs['type'], applicant_id=attrs['applicant_id'])
        if app.exists():
            attrs['app'] = app.first()
        return attrs

    def create(self, validated_data, type):
        return Payment(
            payment_id=UnivPayments.objects.get(payment_title=type),
            applicant_id=validated_data['applicant_id'],
            checkout_id=validated_data['checkout_id'],
            amount=validated_data.get('amount', 0),
            entity_id=validated_data['entity_id'],
            by_cash=validated_data.get('by_cash', False)
        ).save()

    def update(self, instance, validated_data):
        instance.checkout_id = validated_data['checkout_id']
        instance.entity_id = validated_data['entity_id']
        instance.payment_date = datetime.now()
        instance.by_cash = validated_data.get('by_cash', False)
        instance.save()
        return instance


class PayUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "paid", "transaction_id", "amount", "card_number", "authorization_code", "clearing_institute_name",
            "ipCountry", "ipAddr",
        )

    def update(self, instance, validated_data):
        instance.paid = validated_data['paid']
        instance.transaction_id = validated_data['transaction_id']
        instance.amount = validated_data['amount']
        instance.card_number = validated_data['card_number']
        instance.authorization_code = validated_data['authorization_code']
        instance.clearing_institute_name = validated_data['clearing_institute_name']
        instance.ipCountry = validated_data['ipCountry']
        instance.ipAddr = validated_data['ipAddr']
        instance.save()
        return instance


class PayGetSerializer(serializers.ModelSerializer):
    applicant_id = ApplicantListSerializer(read_only=True)
    payment_confirmer = AddUserSerializer(read_only=True)
    type = serializers.CharField(source="payment_id.payment_title", required=False)

    class Meta:
        model = Payment
        fields = ("applicant_id", "checkout_id", 'paid', 'entity_id', 'by_cash', 'payment_confirmer', 'type')
