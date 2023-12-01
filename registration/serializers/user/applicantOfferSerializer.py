from rest_framework import serializers
from ...models.applicant import Applicant


class ApplicantOfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Applicant
        fields = ("offer",)

    def update(self, instance, validated_data):
        instance.offer = validated_data['offer']
        instance.save()
