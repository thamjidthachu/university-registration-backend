from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.models.applicant import Applicant
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.admissionSerializer import ApplicantListSerializer
from registration.signals.applicant import Signal


class Admission(GenericAPIView):
    pagination_class = ApplicantListPagination()
    cache_prefix = "admission_applicants_"

    def get(self, request, *args, **kwargs):
        state = self.request.query_params.get('state', None)
        final_state = self.request.query_params.get('final_state', None)
        major = self.request.query_params.get('major', None)
        semester = self.request.query_params.get('semester', None)
        gender = self.request.query_params.get('gender', None)
        certificate_status = self.request.query_params.get('certificate_status', None)
        cache_name_model = self.cache_prefix + gender + "_" + (
            state + "_" if state is not None else "") + major + "_" + semester + "_model "
        cache_name_serializer = self.cache_prefix + gender + "_" + str(self.request.query_params['page']) + "_" + (
            state + "_" if state is not None else "") + major + "_" + semester + "_serializer"

        applicants = self.get_applicants(self.get_applicant_data, cache_name_model, state, final_state, major, semester, gender, certificate_status)

        query = self.request.query_params.get('query')
        if query not in ["", None]:
            applicants = applicants.filter(
                Q(arabic_full_name__istartswith=query) | Q(arabic_full_name__icontains=query)
                | Q(full_name__istartswith=query) | Q(full_name__icontains=query)
                | Q(national_id__istartswith=query) | Q(email__istartswith=query)
                | Q(family_name__istartswith=query) | Q(emergency_name__istartswith=query)
                | Q(student_id__istartswith=query) | Q(first_name__istartswith=query)

            ).order_by("-registration_date")

        if applicants is None or applicants.count() <= 0:
            return Response({"warning": "No applicants Found",
                             "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        data = self.get_data(ApplicantListSerializer,
                             self.pagination_class.paginate_queryset(applicants, self.request), cache_name_serializer)

        return self.pagination_class.get_paginated_response(data)

    def get_applicant_data(self, state, final_state, major, semester, gender, certificate_status):
        applicants = Applicant.objects.filter(init_state__isnull=False, apply_semester=semester)

        if state not in ['all', '', None]:
            applicants = applicants.filter(init_state__iexact=self.get_init_state(state))

        if final_state not in ['all', '', None]:
            applicants = applicants.filter(final_state=final_state)

        if major not in ['all', '', None]:
            applicants = applicants.filter(major_id__name=major)

        if gender not in ['all', '', None]:
            applicants = applicants.filter(gender=gender)

        if certificate_status not in (None, "", "all"):
            applicants = applicants.filter(certificate_status=certificate_status)

        return applicants.order_by("-registration_date")

    def get_init_state(self, init_state):
        i_state = {
            "under_review": "UR",
            "initial_acceptance": "IA",
            "conditional_acceptance": "CA",
            "rejected": "RJ",
            "Withdrew_Registration": "WR"
        }

        return i_state.get(init_state, None)

    # get data model from the cache
    def get_applicants(self, function, cache_name, *args):
        if Signal.SIGNAL_APPLICANT:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_prefix))
            Signal.SIGNAL_APPLICANT = False

        return CacheModel(function=function, params=args, cache_name=cache_name).get_from_cache()

    # get data serializer from the cache
    def get_data(self, serializer_class, data, cache_name, many=True):
        return CacheSerializer(
            serializer=serializer_class,
            data=data,
            many=many,
            cache_name=cache_name
        ).get_from_cache()
