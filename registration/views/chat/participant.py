from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from registration.models.chat import Participants, Conversation
from registration.serializers.chat.participantSerializer import ListParticipantsSerializer, CreateParticipantsSerializer

from registration.models.user_model import User
from registration.models.applicant import Applicant


class ParticipantView(ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        if 'id' in self.request.query_params:
            user = self.request.session['user']
            participants = ListParticipantsSerializer(self.__get_participant(self.request.query_params['id']),
                                                      many=True).data

            return Response(self.__prepare_data(participants))

        return Response({"error": "Invalid passing the parameters",
                         "error_ar": "خطأ في إرسال البيانات"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if 'participants' in self.request.data and 'conversation_id' in self.request.data:
            if isinstance(self.request.data['participants'], list):
                conversation = self.__get_conversation(self.request.data['conversation_id'])
                if not conversation.exists():
                    return Response({"error": "These conversation isn't found",
                                     "error_ar": "هذه المحادثة غير موجودة"}, status=HTTP_400_BAD_REQUEST)

                for participant in self.request.data['participants']:
                    self.__add_participants(participant, conversation.last())

                return Response("Successfully Added")

        return Response({"error": "Invalid passing the parameters",
                         "error_ar": "خطأ في إرسال البيانات"}, status=HTTP_400_BAD_REQUEST)

    def __get_conversation(self, id):

        return Conversation.objects.filter(id=id)

    def __get_participant(self, id):
        return Participants.objects.filter(conversation__id=id)

    def __prepare_data(self, serializer):

        for ser in serializer:

            user = self.__get_user_name(ser['user'], ser['user_type'])
            ser['name'] = user['name']
            ser['user_type'] = user['type']

        return serializer

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

    def __add_participants(self, participant, conversation):

        check = Participants.objects.filter(**participant)
        if check.exists():
            check.last().conversation.add(conversation)

        else:
            particip = CreateParticipantsSerializer(data=participant)
            particip.is_valid(raise_exception=True)
            particip = particip.save()
            particip.conversation.add(conversation)

        return True
