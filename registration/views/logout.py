from rest_framework.generics import CreateAPIView
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from tokens.views.tokenGenerator import token_generator


class Logout(CreateAPIView):

    def post(self, request, *args, **kwargs):

        token_generator.destroy_user_token(self.request.headers.get('auth-session'))

        return Response("Successfully logged out", status=HTTP_200_OK)
