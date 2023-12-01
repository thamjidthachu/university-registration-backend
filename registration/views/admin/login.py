from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK
from ...serializers.admin.loginAdminSerializer import LoginAdminSerializer
from tokens.views.tokenGenerator import token_generator
from ...models.user_model import User


class LoginAdmin(GenericAPIView):
    serializer_class = LoginAdminSerializer

    def post(self, request, *args, **kwargs):
        login = LoginAdminSerializer(data=self.request.data)
        login.is_valid(raise_exception=True)
        user = self.get_queryset(self.request.data.get('email'))
        token = token_generator.make_token({"pk": user.id, "username": user.full_name, "user_type": 'admin'})
        return Response("Done", status=HTTP_200_OK, headers={"auth-session": token})

    def get_queryset(self, email=None, pk=None):
        try:
            if email is not None:
                return User.objects.get(email__iexact=email)

            if pk is not None:
                return User.objects.get(id=pk)
        except User.DoesNotExist:
            return None

