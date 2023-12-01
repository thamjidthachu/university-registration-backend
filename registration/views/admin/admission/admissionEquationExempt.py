from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from registration.models.applicant import Applicant
from registration.models.user_model import User
from registration.serializers.admin.admissionSerializer import ApplicantEquationFees


class EquationFeesExemptView(UpdateAPIView):
    queryset = Applicant
    serializer_class = ApplicantEquationFees
    
    def put(self, request, *args, **kwargs):
        if self.get_current_user(int(self.request.session['user']['pk'])).role not in [6, 2]:
            return Response({"error": "You don't have access.",
                             "error_ar": "ليس لديك صلاحية."}, status=400)
        self.partial_update(request, *args, **kwargs)
        return Response({"success": "Updated Successfully.",
                         "success_ar": "تم التحديث بنجاح."})

    def get_current_user(self, user_pk):
        return User.objects.get(pk=user_pk)