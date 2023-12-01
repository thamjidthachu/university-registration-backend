from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from registration.serializers.chat.messageSerializer import ListMessageSerializer, CreateMessageSerializer
from registration.models.chat import Message, Conversation, Participants, MessageParticipants
from registration.models.user_model import User
from registration.models.applicant import Applicant
from university.pusher import pusher_client
from registration.pagination.applicantListPagination import ApplicantListPagination


class MessageView(ListCreateAPIView):
    pagination_class = ApplicantListPagination()

    def post(self, request, *args, **kwargs):
        if 'type' in kwargs and kwargs['type'] in ['add', 'retrieve']:
            if kwargs['type'] == 'add':

                if ("conversation" in self.request.data and isinstance(self.request.data['conversation'], dict) and
                        "message" in self.request.data and "message_type" in self.request.data):
                    return self.__add_message(self.request)

                return Response({"error": "Invalid passing the parameters"}, status=HTTP_400_BAD_REQUEST)

            elif kwargs['type'] == 'retrieve':

                if "conversation" in self.request.data and isinstance(self.request.data['conversation'], dict):
                    return self.__retrieve_messages(request)

                return Response({"error": "Invalid passing the parameters"}, status=HTTP_400_BAD_REQUEST)

        return Response({"details": "Method not allowed"}, status=HTTP_400_BAD_REQUEST)

    def __retrieve_messages(self, request):
        if 'conversation' in request.data and isinstance(request.data['conversation'], dict):
            conversation = request.data['conversation']
            channel = "room-" + str(conversation['applicant_id']) + "-" + str(conversation['user_role'])
            messages = self.__get_messages(channel)

            if not messages.exists():
                return Response([])

            pg_messages = self.pagination_class.paginate_queryset(messages, request)
            data = ListMessageSerializer(pg_messages, many=True).data

            pusher_client.trigger(f'{messages.last().conversation.channel_name}', 'get_messages',
                                  {"count": self.pagination_class.page.paginator.count,
                                   "next": self.pagination_class.get_next_link(),
                                   "previous": self.pagination_class.get_previous_link(),
                                   "results": data})

            # should be get conversation id and message text followed by message type
            return Response("Done")

        return Response({"error": "Invalid passing the paramters",
                         "error_ar": "خطأ في إرسال البيانات"},
                        status=HTTP_400_BAD_REQUEST)

    def __add_message(self, request):

        user = self.request.session['user']
        user_type = 2 if user['user_type'] == 'admin' else 1

        # get or create conversation

        conversation = self.get_or_create_conversation(request.data['conversation'], user['pk'], user_type)
        if conversation is None:
            return Response({"error": "These conversation isn't found"}, status=HTTP_400_BAD_REQUEST)

        message = CreateMessageSerializer(data={"message": request.data['message'],
                                                "message_type": request.data['message_type'],
                                                "conversation": conversation})
        message.is_valid(raise_exception=True)
        message = message.save()
        participants = Participants.objects.filter(conversation__id=message.conversation.id)
        send_message = []
        for participant in participants:
            if participant.user == user['pk'] and participant.user_type == user_type:
                send_message.append(
                    MessageParticipants(message=message, participant=participant, receiver=False, seen=True,
                                        delivered=True))
            else:
                send_message.append(
                    MessageParticipants(message=message, participant=participant))
        MessageParticipants.objects.bulk_create(send_message)
        pusher_client.trigger(f'{message.conversation.channel_name}', 'send_message',
                              {"message": message.message,
                               "message_type": message.message_type,
                               "seen": message.seen,
                               "user_type": user_type,
                               "name": user['username'],
                               "id": user['pk'],
                               "delivered": message.delivered})

        return Response("Successfully added")

    def __get_conversation(self, id):

        return Conversation.objects.get(id=id).messages.all().order_by('-created')

    def __get_user(self, id, user_type):
        if user_type == "admin":
            return User.objects.filter(id=id)

        return Applicant.objects.filter(id=id)

    def __get_messages(self, channel):
        return Message.objects.filter(conversation__channel_name=channel).order_by('-created')

    def get_user_by_role(self, role):
        return User.objects.filter(role=role)

    def get_or_create_conversation(self, conversation, id, user_type):

        from registration.serializers.chat.conversationSerializer import CreateConversationSerializer
        from registration.models.chat import Participants

        channel = "room-" + str(conversation['applicant_id']) + "-" + str(conversation['user_role'])

        participant = Participants.objects.filter(conversation__channel_name=channel)

        if participant.exists():

            return participant.last().conversation.all().last().id

        else:

            user_creator = id
            user_type_creator = user_type
            conversation_type = 2
            conv = CreateConversationSerializer(data={"channel_name": channel,
                                                      "name": conversation['name'],
                                                      "user_creator": user_creator,
                                                      "user_type_creator": user_type_creator,
                                                      "conversation_type": conversation_type})
            conv.is_valid(raise_exception=True)
            conv = conv.save()

            admins = self.get_user_by_role(conversation['user_role'])
            if not admins.exists():
                return

            for admin in admins:
                if admin.id == id and user_type == 2:
                    self.__create_participants({"user": admin.id,
                                                "user_type": 2,
                                                "is_admin": True}, conv)
                else:
                    self.__create_participants({"user": admin.id,
                                                "user_type": 2}, conv)

            if user_type == 1:
                self.__create_participants({"user": conversation['applicant_id'],
                                            "user_type": 1,
                                            "is_admin": True}, conv)
            else:
                self.__create_participants({"user": conversation['applicant_id'],
                                            "user_type": 1}, conv)

        return conv.id

    def __create_participants(self, participant, conversation):
        from registration.serializers.chat.participantSerializer import CreateParticipantsSerializer
        from registration.models.chat import ConversationParticipants
        is_admin = False
        if 'is_admin' in participant:
            participant.pop('is_admin')
            is_admin = True

        particip = CreateParticipantsSerializer(data=participant)
        particip.is_valid(raise_exception=True)
        particip = particip.save()
        ConversationParticipants(conversation=conversation, participant=particip, is_admin=is_admin).save()

        return True
