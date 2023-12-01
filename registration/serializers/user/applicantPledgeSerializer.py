from rest_framework import serializers
from ...models.applicant import Applicant


class ApplicantPledgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Applicant
        fields = ("pledge",)

    def update(self, instance, validated_data):
        instance.pledge = validated_data['pledge']
        instance.save()
