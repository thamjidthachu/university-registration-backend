from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.generics import UpdateAPIView
from tokens.views.tokenGenerator import token_generator
from ...serializers.user.updatePasswordSerializer import UpdatePasswordSerializer


class UpdatePassword(UpdateAPIView):

    def put(self, request, *args, **kwargs):

        if "token" in self.request.query_params:
            token = self.request.query_params['token']
            applicant = self.get_applicant_token(token)
            if applicant is None:
                return Response("This token is expired", status=HTTP_400_BAD_REQUEST)

            if not token_generator.check_token(token, applicant, timeout_min=10):
                self.request.data['id'] = int(applicant['pk'])
                app = UpdatePasswordSerializer(data=self.request.data)
                app.is_valid(raise_exception=True)
                app.update(app.validated_data['applicant'], app.validated_data)
                token_generator.destroy_user_token(token)
                return Response("successfully updated", status=HTTP_200_OK)

            token_generator.destroy_user_token(token)
            return Response("This token is expired", status=HTTP_400_BAD_REQUEST)

        return Response("Invalid access this link", status=HTTP_404_NOT_FOUND)

    def get_applicant_token(self, token):
        return token_generator.get_user_from_hash(token)
