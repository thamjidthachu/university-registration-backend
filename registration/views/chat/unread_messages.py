from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from university.pusher import pusher_client
from registration.models.chat import MessageParticipants
from registration.serializers.chat.messageParticipantSerializer import ListMessageParticipantSerializer
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination


class UnreadMessages(RetrieveAPIView):
    pagination_class = ApplicantListPagination()

    def get(self, request, *args, **kwargs):
        user = self.request.session['user']
        user_type = 2 if user['user_type'] == 'admin' else 1
        messages = self.get_messages(user['pk'], user_type)
        user_role = self.get_user_role(user['pk']) if user_type == 2 else 1

        count = messages.count()
        pg_messages = self.pagination_class.paginate_queryset(messages, self.request)
        messages = ListMessageParticipantSerializer(pg_messages, many=True).data
        pusher_client.trigger('unread-messages', f"{user['pk']}-{user_role}",
                              {"count": count,
                               "pages_count": self.pagination_class.page.paginator.count,
                               "next": self.pagination_class.get_next_link(),
                               "previous": self.pagination_class.get_previous_link(),
                               "results": messages})
        return Response("Done", status=HTTP_200_OK)

    def get_messages(self, id, user_type):
        return MessageParticipants.objects.filter(participant__user=id, participant__user_type=user_type,
                                                  seen=False, delivered=False)

    def get_user_role(self, id):
        return User.objects.get(id=id).role
