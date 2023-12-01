from django.db.models import Q
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from registration.models.applicant import Applicant
from registration.models.chat import Conversation, Participants, ConversationParticipants
from registration.models.user_model import User
from registration.serializers.chat.conversationSerializer import ListConversationSerializer, \
    CreateConversationSerializer
from registration.serializers.chat.participantSerializer import CreateParticipantsSerializer


class ConversationView(ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        user = self.request.session['user']
        user_type = 1 if user['user_type'] == 'admin' else 2
        conversations = self.__get_conversation(user['pk'], user_type)
        if conversations:
            convSerializer = ListConversationSerializer(conversations, many=True).data

            return Response(self.__prepare_data(conversations, convSerializer, user['pk'], user_type))

        return Response([])

    def post(self, request, *args, **kwargs):
        if 'participants' in self.request.data:
            user = self.request.session['user']
            if not isinstance(self.request.data['participants'], list):
                return Response({"error": "Invalid passing the parameters",
                                 "error_ar": "خطأ في إرسال المعلومات"}, status=HTTP_400_BAD_REQUEST)

            if ((len(self.request.data['participants']) > 1)
                    and self.request.data['conversation']['conversation_type'] == 1):
                return Response({"error": "The private conversation should only one participant not group of participants",
                                 "error_ar": "المحادثة الخاصة يجب ان يشارك بها عضو واحد فقط وليس مجموعة من الاعضاء"},
                                status=HTTP_400_BAD_REQUEST)

            self.request.data['conversation']['channel_name'] = "room-"
            self.request.data['conversation']['user_type_creator'] = 2 if user['user_type'] == 'admin' else 1
            self.request.data['conversation']['user_creator'] = user['pk']
            conversation = CreateConversationSerializer(data=self.request.data['conversation'])
            conversation.is_valid(raise_exception=True)
            conversation = conversation.save()
            participants = self.request.data['participants']
            creator = {"user": user['pk'],
                                 'user_type': 1 if user['user_type'] == 'admin' else 2, 'is_admin': True}

            participants.append(creator)

            for participant in participants:
                self.__create_or_update_particpant(participant, conversation)

            return Response("Successfully Created")

        return Response({"error": "Invalid passing the data", "error_ar": "خطأ في إرسال البيانات"}, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self, id, user_type):
        return Conversation.objects.filter(user__user=id, user__user_type__exact=user_type)

    def __get_conversation(self, id, user_type):
        try:

            return Participants.objects.get(user=id, user_type=user_type).conversation.all().order_by("-created")

        except Participants.DoesNotExist:
            return

    def __prepare_data(self, conversation, serializer, id, user_type):

        for index, key in enumerate(conversation):
            if key.conversation_type == 1:
                another = self.__another_participant(id, user_type, key.id)
                if another:
                    user = self.__get_user_name(another.user, another.user_type)
                    serializer[index]['name'] = user['name']
                    serializer[index]['type'] = user['type']

        return serializer

    def __another_participant(self, id, user_type, conv_id):
        try:

            return Participants.objects.get(~Q(user=id, user_type=user_type) &
                                            Q(conversation__id=conv_id))

        except Participants.DoesNotExist:
            return

    def __get_user_name(self, id, user_type):
        if user_type == 1:
            user = User.objects.get(id=id)
            return {"name": user.userName, "type": dict(User.USER_ROLES)[user.role]}
        else:
            app = Applicant.objects.get(id=id)
            return {
                "name": app.first_name + " " + app.last_name,
                "type": "Applicant"
            }

    def __get_user(self, id, user_type):
        if user_type == 1:
            return User.objects.get(id=id)

        return Applicant.objects.get(id=id)

    def __create_or_update_particpant(self, participant, conversation):
        is_admin = False
        if 'is_admin' in participant:
            participant.pop('is_admin')
            is_admin = True

        check = Participants.objects.filter(**participant)
        if check.exists():
            ConversationParticipants(conversation=conversation, participant=check.last(), is_admin=is_admin).save()
        else:
            particip = CreateParticipantsSerializer(data=participant)
            particip.is_valid(raise_exception=True)
            particip = particip.save()
            ConversationParticipants(conversation=conversation, participant=particip, is_admin=is_admin).save()

        return True
