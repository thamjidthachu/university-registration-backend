from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from registration.models.chat import Message, MessageParticipants
from university.pusher import pusher_client


class SeenView(CreateAPIView):

    def post(self, request, *args, **kwargs):
        if 'conversation' in self.request.data:

            user = self.request.session['user']
            seen = self.get_message(self.request.data['conversation'])
            if seen.exists():
                self.change_to_seen(seen, user['pk'])
                pusher_client.trigger(f'{seen.last().conversation.channel_name}', 'seen_message', {"seen": True})
                return Response("seen", status=HTTP_200_OK)
            return Response("this message isn't found!", status=HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid parameters!"}, status=HTTP_400_BAD_REQUEST)

    def get_message(self, conversation):

        channel = "room-" + str(conversation['applicant_id']) + "-" + str(conversation['user_role'])
        return Message.objects.filter(conversation__channel_name=channel)

    def change_to_seen(self, messages, user_id):
        for message in messages:
            MessageParticipants.objects.filter(participant_id=user_id, message_id=message.id).update(seen=True)

            seen = MessageParticipants.objects.filter(message_id=message.id)
            if seen.exists():
                if seen.count() == seen.filter(seen=True).count():
                    d = seen.last()
                    d.message.seen = True
                    d.message.save()

        return True
