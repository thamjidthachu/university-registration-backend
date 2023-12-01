from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.models.evaluation import EnglishTest
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.englishGradeSerializer import EnglishListSerializer
from registration.signals.english import Signal


class EnglishConfirmData(GenericAPIView):
    pagination_class = ApplicantListPagination()
    cache_name_prefix = "english_"

    def get(self, request, *args, **kwargs):

        state = self.request.query_params.get('state', None)
        major = self.request.query_params.get('major', None)
        semester = self.request.query_params.get('semester', None)
        gender = self.request.query_params.get('gender', None)
        trail = self.request.query_params.get('trail', None)
        date_from = self.request.query_params.get('from', None)
        date_to = self.request.query_params.get('to', None)

        cache_name_model = self.cache_name_prefix + "conformer_" + (state + "_" if state is not None else "") + (
            gender + "_" if gender is not None else "") + major + "_" + semester + "_model"

        cache_name_serializer = self.cache_name_prefix + "conformer_" + str(self.request.query_params['page']) + "_" + (
            state + "_" if state is not None else "") + "_" + (
                                    gender + "_" if gender is not None else "") + major + "_" + semester + "_serializer"

        english = self.get_applicants(self.get_english_queryset, cache_name_model, state, gender, trail, major, semester, date_from, date_to)

        query = self.request.query_params.get('query')
        if query not in ["", None]:
            english = english.filter(
                Q(applicant_id__national_id__istartswith=query) | Q(applicant_id__arabic_full_name__istartswith=query)
                | Q(applicant_id__full_name__istartswith=query) | Q(applicant_id__email__istartswith=query)
                | Q(applicant_id__arabic_last_name__icontains=query) | Q(applicant_id__last_name__icontains=query)
            ).order_by("-reservation_id__reservation_date")

        if english is None or english.count() <= 0:
            return Response({"warning": "No applicants Found", "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        applicant_data_pagination = self.pagination_class.paginate_queryset(
            english,
            self.request
        )

        applicants = self.get_data(EnglishListSerializer, applicant_data_pagination, cache_name_serializer, many=True)

        return self.pagination_class.get_paginated_response(applicants)

    def get_english_queryset(self, state, gender, trail, major, semester, date_from=None, date_to=None):
        english_test_qs = EnglishTest.objects.filter(
            result="S", applicant_id__apply_semester=semester, paid=True,
        ).exclude(applicant_id__major_id__name='NM')

        if state not in ['all', '', None]:
            english_test_qs = english_test_qs.filter(confirmed=self.get_result_filter(state))

        if major not in ['all', '', None]:
            english_test_qs = english_test_qs.filter(applicant_id__major_id__name=major)

        if gender not in ['all', '', None]:
            english_test_qs = english_test_qs.filter(applicant_id__gender=gender)

        if trail not in ['all', None, '']:
            english_test_qs = english_test_qs.filter(test_try=trail)

        if date_from not in ['all', None, ''] and date_to not in ['all', None, '']:
            english_test_qs = english_test_qs.filter(reservation_id__reservation_date__gte=date_from, reservation_id__reservation_date__lte=date_to)

        return english_test_qs.order_by("-reservation_id__reservation_date")

    def get_result_filter(self, state):
        result = {
            "not_graded": False,
            "confirmed": True
        }

        return result.get(state, -1)

    def get_user(self, pk):
        return User.objects.get(id=pk)

    def get_applicants(self, function, cache_name, *args, **kwargs):
        if Signal.SIGNAL_ENGLISH:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_name_prefix))
            Signal.SIGNAL_ENGLISH = False

        return CacheModel(function=function, params=args, kwargs=kwargs, cache_name=cache_name).get_from_cache()

    def get_data(self, serializer_class, data, cache_name, many=True):
        return CacheSerializer(serializer=serializer_class, data=data,
                               cache_name=cache_name, many=many).get_from_cache()
