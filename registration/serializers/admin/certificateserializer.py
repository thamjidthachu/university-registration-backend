from rest_framework import serializers

from registration.models.applicant import Certificate, Applicant
from registration.serializers.admin.admissionSerializer import AddUserSerializer


class ApplicantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = (
            "id", "full_name", "arabic_full_name", "apply_semester", "applicant_type", 'email', 'phone', 'national_id')


class CreateCertificateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ("applicant", "name",)


class SubmitCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ("status", "approve_user",)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.approve_user = validated_data['approve_user']
        instance.save()
        return instance


class RetrieveCertificateSerializer(serializers.ModelSerializer):
    applicant = ApplicantProfileSerializer()
    approve_user = AddUserSerializer()

    class Meta:
        model = Certificate
        fields = ['applicant', 'name', 'approve_user', 'status', 'created_date', 'modified_date']
