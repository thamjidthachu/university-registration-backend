from rest_framework import serializers
from registration.models.chat import MessageParticipants, Message
from .messageSerializer import UnreadMessageSerializer


class ListMessageParticipantSerializer(serializers.ModelSerializer):
    message = UnreadMessageSerializer()

    class Meta:
        model = MessageParticipants
        fields = ('message',)
