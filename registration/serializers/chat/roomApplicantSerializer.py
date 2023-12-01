from rest_framework import serializers
from ...models.applicant import Applicant


class RoomListApplicantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Applicant
        fields = ('id', 'full_name', 'national_id',)
