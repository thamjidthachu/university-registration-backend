from rest_framework import serializers
from registration.models.chat import Participants


class CreateParticipantsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participants
        fields = ('user', 'user_type',)


class ListParticipantsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participants
        fields = ('user', 'user_type',)
