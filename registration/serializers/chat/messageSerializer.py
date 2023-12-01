from rest_framework import serializers
from registration.models.chat import Message, MessageParticipants
from registration.models.user_model import User
from registration.models.applicant import Applicant


class MessageSerializer(serializers.ModelSerializer):

    error_msg = {
        "message": {"Invalid sending a message!"},
    }

    class Meta:
        model = Message
        fields = "__all__"

    def validate(self, attrs):
        if not User.objects.filter(id=attrs['sender']).exists():
            if not Applicant.objects.filter(id=attrs['sender']).exists():
                raise serializers.ValidationError(self.error_msg['message'])

        if not Applicant.objects.filter(id=attrs['receiver']).exists():
            if not User.objects.filter(id=attrs['receiver']).exists():
                raise serializers.ValidationError(self.error_msg['applicant'])

        return attrs


class ListMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'message', 'message_type', 'seen', 'delivered',)

    def to_representation(self, instance):
        represented = super().to_representation(instance)
        message = MessageParticipants.objects.filter(message_id=represented['id'], receiver=False)
        sender = message.last().participant
        represented['id'] = sender.user
        represented['user_type'] = sender.user_type

        if sender.user_type == 2:
             represented['name'] = User.objects.get(id=sender.user).userName

        else:
            app = Applicant.objects.get(id=sender.user)
            represented['name'] = app.first_name + " " + app.last_name

        return represented


class CreateMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = "__all__"


class UnreadMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'message', 'conversation',)

    def to_representation(self, instance):
        represented = super(UnreadMessageSerializer, self).to_representation(instance)

        message = MessageParticipants.objects.get(receiver=False, message_id=represented['id'])

        if message.participant.user_type == 2:
            user = User.objects.get(id=message.participant.user)
            name = user.userName
            user_role = user.role

        else:
            user = Applicant.objects.get(id=message.participant.user)
            name = user.first_name + " " + user.last_name
            user_role = 1

        represented['message'] = {
            "message": message.message.message,
            "sender": name,
            "user_role": user_role,
        }

        represented['conversation'] = message.message.conversation.name

        return represented
