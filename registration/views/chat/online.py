from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from university.pusher import pusher_client
from registration.models.chat import Participants
from django.utils.timezone import now
from registration.models.user_model import User


class OnlineView(RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        if 'online' in self.request.query_params:
            is_online = True if self.request.query_params['online'] == 'true' else False
            user = self.request.session['user']
            if user['user_type'] == 'admin':
                user_role = self.get_user(user['pk']).role
            else:
                user_role = 2
            participant = self.get_participant(user['pk'], 2 if user['user_type'] == 'admin' else 1)

            if participant.exists():
                if is_online:
                    participant.update(is_online=is_online, last_online=None)
                else:
                    participant.update(is_online=is_online, last_online=now())

                pusher_client.trigger('online', '', {"online": is_online,
                                                     "name": user['username'],
                                                     "user_role": user_role,
                                                     "user": user['pk'],
                                                     "last_online": str(
                                                         participant.last().last_online.strftime("%d-%m-%y %H:%M:%S"))})

                return Response("Done", status=HTTP_200_OK)

        return Response("this conversation isn't found!", status=HTTP_400_BAD_REQUEST)

    def get_participant(self, id, user_type):
        return Participants.objects.filter(user=id, user_type=user_type)

    def get_user(self, id):
        return User.objects.get(id=id)
