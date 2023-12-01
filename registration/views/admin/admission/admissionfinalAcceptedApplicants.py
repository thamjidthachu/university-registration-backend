from django.db.models import Q, F, Count
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.models.applicant import Applicant, Certificate
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.admissionSerializer import ApplicantFinalAcceptSerializer
from registration.signals.applicant import Signal


class finalAcceptedApplicants(GenericAPIView):
    pagination_class = ApplicantListPagination()
    cache_name_prefix = "admission_applicants_accepted_"

    def get(self, request, *args, **kwargs):

        if {'semester', 'major', 'gender'} <= request.query_params.keys():
            state = request.query_params.get('state', None)
            major = request.query_params.get('major', None)
            semester = request.query_params.get('semester', None)
            gender = request.query_params.get('gender', None)
            certificate_status = request.query_params.get('certificate_status', None)
            date_from = request.query_params.get('from', None)
            date_to = request.query_params.get('to', None)

            cache_name_model = self.cache_name_prefix + gender + "_" + state if state else "" + "_" + major + "_" + semester + "_model"
            cache_name_serializer = self.cache_name_prefix + str(request.query_params['page']) + "_" + gender + "_" + state if state else "" + "_" + major + "_" + semester + "_serializer"

            applicants = self.get_applicants(
                self.get_applicant_data, cache_name_model, gender, semester, major, state, certificate_status, date_from, date_to
            ).order_by(F("final_state_date").desc(nulls_last=True))

            query = request.query_params.get('query')
            if query not in ["", None]:
                applicants = applicants.filter(
                    Q(national_id__istartswith=query) | Q(arabic_full_name__istartswith=query)
                    | Q(full_name__istartswith=query) | Q(email__istartswith=query)
                    | Q(arabic_last_name__icontains=query) | Q(last_name__icontains=query)
                )

            if applicants is None or applicants.count() <= 0:
                return Response({"warning": "No applicants Found",
                                 "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

            return self.pagination_class.get_paginated_response(
                self.get_data(ApplicantFinalAcceptSerializer,
                              self.pagination_class.paginate_queryset(
                                  applicants, request),
                              cache_name_serializer, )

            )
        return Response({"ERROR": "Invalid access this link", "warning_ar": "خطأ فى امكانية الاتصال "},
                        status=HTTP_404_NOT_FOUND)

    @staticmethod
    def get_current_user(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_applicant_data(gender, semester, major, state='A', certificate_status=None, date_from=None, date_to=None):
        queryset = Applicant.objects.filter(apply_semester=semester)

        if state not in (None, "", "all"):
            queryset = queryset.filter(final_state__exact=state)

        if gender not in (None, "", "all"):
            queryset = queryset.filter(gender=gender)

        if major not in (None, "", "all"):
            queryset = queryset.filter(major_id__name=major)

        if date_from and date_to:
            queryset = queryset.filter(final_state_date__date__range=(date_from, date_to))

        if certificate_status not in (None, "", "all"):
            queryset = queryset.filter(certificate_status=certificate_status)

        return queryset

    def get_applicants(self, function, cache_name, *args, **kwargs):
        if Signal.SIGNAL_APPLICANT:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_name_prefix))
            Signal.SIGNAL_APPLICANT = False

        return CacheModel(
            function=function,
            params=args,
            kwargs=kwargs,
            cache_name=cache_name,
        ).get_from_cache()

    @staticmethod
    def get_data(serializer_class, data, cache_name, many=True):
        return CacheSerializer(
            serializer=serializer_class,
            data=data,
            cache_name=cache_name, many=many
        ).get_from_cache()
