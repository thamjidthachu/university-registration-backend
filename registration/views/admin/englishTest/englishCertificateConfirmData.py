from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from registration.models.applicant import Applicant
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.englishGradeSerializer import EnglishCertificateListSerializer


class EnglishCertificateConfirm(GenericAPIView):
    pagination_class = ApplicantListPagination()

    def get(self, request, *args, **kwargs):
        state = self.request.query_params.get('state', None)
        major = self.request.query_params.get('major', None)
        semester = self.request.query_params.get('semester', None)

        applicants = self.get_applicants(state, major, semester)

        query = self.request.query_params.get('query')
        if query not in ["", None]:
            applicants = applicants.filter(
                Q(arabic_full_name__istartswith=query) | Q(full_name__istartswith=query) | Q(email__istartswith=query) |
                Q(national_id__istartswith=query) | Q(arabic_last_name__icontains=query) | Q(last_name__icontains=query)
            ).order_by("-registration_date")

        if applicants is None or applicants.count() <= 0:
            return Response({"warning": "No applicants Found", "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        query = self.pagination_class.paginate_queryset(applicants, self.request)

        return self.pagination_class.get_paginated_response(EnglishCertificateListSerializer(query, many=True).data)

    def get_applicants(self, state, major, semester):
        query_set = Applicant.objects.filter(
            apply_semester=semester, english_certf_result="S"
        ).exclude(major_id__name='NM').order_by("-registration_date")

        if state not in ["all", "", None]:
            query_set = query_set.filter(english_certf_confirmation=self.get_result_filter(state))
        if major not in ["all", "", None]:
            query_set = query_set.filter(major_id__name=major)

        return query_set

    @staticmethod
    def get_result_filter(state):
        result = {
            "not_graded": False,
            "confirmed": True,
        }
        if state in result:
            return result[state]

        return -1

    @staticmethod
    def get_user(user_id):
        return User.objects.get(id=user_id)
