from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from registration.serializers.admin.admissionSerializer import UpdateRoleSerializer
from registration.models.user_model import User


class UpdateRole(UpdateAPIView):

    def put(self, request):

        user = User.objects.get(id = int(self.request.session['user']['pk']))
        admin = UpdateRoleSerializer(user, data=self.request.data)
        admin.is_valid(raise_exception=True)
        admin.update(user, admin.validated_data)
        return Response({"success": "Role Updated successfully",
                                            "success_ar": "تم تعديل الصلاحية بنجاح"},status=200)
