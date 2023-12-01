from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from registration.models.chat import Conversation
from university.pusher import pusher_client


class TypingView(RetrieveAPIView):

    def post(self, request, *args, **kwargs):
        if 'conversation' in self.request.data and 'typing' in self.request.query_params:

            user = self.request.session['user']
            conversation = self.get_conversation(self.request.data['conversation'])
            if conversation.exists():
                typing = True if self.request.query_params['typing'] == "true" else False
                pusher_client.trigger(f'{conversation.last().channel_name}', 'typing', {"typing": typing,
                                                                                        "name": user['username']})
                return Response("Done", status=HTTP_200_OK)
            return Response("this conversation isn't found!", status=HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid parameters!"}, status=HTTP_400_BAD_REQUEST)

    def get_conversation(self, conversation):

        channel = "room-" + str(conversation['applicant_id']) + "-" + str(conversation['user_role'])
        return Conversation.objects.filter(channel_name=channel)
