from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from registration.models.chat import Message, MessageParticipants
from university.pusher import pusher_client


class DeliveredView(CreateAPIView):

    def post(self, request, *args, **kwargs):

        # remove conversation and handle all conversation with delivered true when open
        if 'conversation' in self.request.data:

            user = self.request.session['user']
            delivered = self.get_queryset(self.request.data['conversation'])
            if delivered.exists():
                self.change_to_delivered(delivered, user['pk'])
                pusher_client.trigger(f'{delivered.last().conversation.channel_name}', 'delivered_message',
                                      {"delivered": True})
                return Response("delivered", status=HTTP_200_OK)
            return Response("this message isn't found!", status=HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid parameters!"}, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self, conversation):

        channel = "room-" + str(conversation['applicant_id']) + "-" + str(conversation['user_role'])
        return Message.objects.filter(conversation__channel_name=channel)

    def change_to_delivered(self, messages, user_id):

        for message in messages:
            MessageParticipants.objects.filter(participant_id=user_id, message_id=message.id).update(delivered=True)

            delivered = MessageParticipants.objects.filter(message_id=message.id)
            if delivered.exists():
                if delivered.count() == delivered.filter(delivered=True).count():
                    d = delivered.last()
                    d.message.delivered = True
                    d.message.save()

        return True
