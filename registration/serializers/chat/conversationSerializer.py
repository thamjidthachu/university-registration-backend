from rest_framework import serializers
from registration.models.chat import Conversation, Participants


class ListConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = ['id', 'name']


class CreateConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = "__all__"
