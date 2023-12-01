from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from registration.serializers.admin.admissionSerializer import AbsentApplicantSerializer
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.models.evaluation import Absent
from django.db.models import Q
from registration.models.user_model import User


class absentApplicants(GenericAPIView):
    pagination_class = ApplicantListPagination()

    def get(self, request, *args, **kwargs):
        if ("type" in self.request.query_params or 'query' in self.request.query_params) and "semester" in self.request.query_params:
            user = self.get_user(int(self.request.session['user']['pk']))
            if user.exists():
                gender = user.first().gender
                type = int(self.request.query_params['type'])
                state = self.request.query_params.get('state', None)
                major = self.request.query_params.get('major', None)
                semester = self.request.query_params.get('semester', None)
                gender = self.request.query_params.get('gender', None)
                date_from = self.request.query_params.get('from', None)
                date_to = self.request.query_params.get('to', None)
                applicants_data = self.get_applicants(type, semester, state, major, gender, date_from, date_to)

                query = self.request.query_params.get('query')
                if query not in ["", None]:
                    applicants_data = applicants_data.filter(
                        Q(applicant_id__arabic_full_name__istartswith=query)
                        | Q(applicant_id__full_name__istartswith=query)
                        | Q(applicant_id__national_id__istartswith=query)
                        | Q(applicant_id__email__istartswith=query)
                        | Q(applicant_id__arabic_last_name__icontains=query)
                        | Q(applicant_id__last_name__icontains=query)
                    )
                applicants = AbsentApplicantSerializer(applicants_data, many=True).data
                if not applicants:
                    return Response(
                        {"warning": "No applicants Found",
                         "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND
                    )

                applicant_data_pagination = self.pagination_class.paginate_queryset(applicants, self.request)

                return self.pagination_class.get_paginated_response(applicant_data_pagination)

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_404_NOT_FOUND)
        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)

    def get_user(self, user_id):
        try:
            return User.objects.filter(id=user_id)
        except User.DoesNotExist:
            return None

    from django.db.models import Q

    def get_applicants(self, gender, type, semester, state, major, date_from=None, date_to=None):
        filter_args = Q(applicant_id__apply_semester=semester, applicant_id__init_state__isnull=False,
                        reservation_id__test_type=type)

        if state == 'eval':
            filter_args &= Q(applicant_id__init_state__in=["IA", "CA"])
        elif state not in ['all', '', None]:
            filter_args &= Q(applicant_id__init_state__exact=state)

        if major not in ['all', '', None]:
            filter_args &= Q(applicant_id__major_id__name=major)

        if gender not in ['all', '', None]:
            filter_args &= Q(applicant_id__gender=gender)

        if date_from is not None and date_to is not None:
            filter_args &= Q(reservation_id__reservation_date__range=[date_from, date_to])

        return Absent.objects.filter(filter_args)
