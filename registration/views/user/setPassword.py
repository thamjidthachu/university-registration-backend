from rest_framework.generics import GenericAPIView

from ..currentUserInfo import currentUserInfo
from ...serializers.user.loginSerializer import SetPassowrdSerializer


class SetPassword(GenericAPIView):

    def post(self, request, *args, **kwargs):
        password = SetPassowrdSerializer(data=self.request.data)
        password.is_valid(raise_exception=True)
        app = password.update(password.validated_data['applicant'], password.validated_data)

        return currentUserInfo().get_applicant_data(app)
