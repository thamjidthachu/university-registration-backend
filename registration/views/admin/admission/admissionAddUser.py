from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from registration.models.user_model import User
from registration.serializers.admin.admissionSerializer import AddUserSerializer


class AddUser(GenericAPIView):

    def get(self, request, *args, **kwargs):
        users = AddUserSerializer(self.get_all_users(), many=True).data
        return Response({"users": users}, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = AddUserSerializer(data=self.request.data)
        user.is_valid(raise_exception=True)
        user.save()
        users = AddUserSerializer(self.get_all_users(), many=True).data

        return Response({"users": users}, status=HTTP_200_OK)

    def get_all_users(self):
        return User.objects.filter(role=11)
