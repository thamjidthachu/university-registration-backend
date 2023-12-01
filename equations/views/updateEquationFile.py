from rest_framework.generics import UpdateAPIView
from equations.models import Equation
from equations.serializers.equationSerializer import EquationFileSerializer


class UpdateEquationFile(UpdateAPIView):
    queryset = Equation
    serializer_class = EquationFileSerializer

    def get_serializer(self, request, *args, **kwargs):
        return super().get_serializer(request, *args, **kwargs, context={'user': self.request.session['user']})
