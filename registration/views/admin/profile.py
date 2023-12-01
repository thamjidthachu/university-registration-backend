from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.generics import UpdateAPIView
from ...serializers.admin.userProfileSerializer import UserProfileSerializer
from ...models.user_model import User


class AdminProfile(UpdateAPIView):

    def put(self, request, *args, **kwargs):
        if 'id' in self.request.data:
            user = self.get_user(self.request.data['id'])
            profile = UserProfileSerializer(user, data=self.request.data)
            profile.is_valid(raise_exception=True)
            profile.update(user, profile.validated_data)
            return Response("Successfully updated", status=HTTP_200_OK)
        else:
            return Response("Invalid passing data", status=HTTP_400_BAD_REQUEST)

    def get_user(self, id):
        return User.objects.get(id=id)

