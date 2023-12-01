from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_200_OK
from registration.serializers.user.loginSerializer import LoginSerializer
from tokens.views.tokenGenerator import token_generator


class Login(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        login = LoginSerializer(data=self.request.data)
        login.is_valid(raise_exception=True)
        app = login.validated_data['applicant']
        token = token_generator.make_token({"pk": app.id, "username": app.full_name, "user_type": 'applicant'})
        return Response({"session": request.session}, status=HTTP_200_OK, headers={"auth-session": token})
