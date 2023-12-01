from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.response import Response
from registration.models.applicant import Applicant
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.englishGradeSerializer import EnglishCertificateListSerializer
from registration.models.user_model import User
from django.db.models import Q
from cache.cacheSerializer import CacheSerializer
from cache.cacheModel import CacheModel
from registration.signals.applicant import Signal


class EnglishCertificate(GenericAPIView):
    pagination_class = ApplicantListPagination()
    cache_name_prefix = "english_applicants_certf_"

    def get(self, request, *args, **kwargs):

        state = self.request.query_params.get('state', None)
        major = self.request.query_params.get('major', None)
        semester = self.request.query_params.get('semester', None)
        gender = self.request.query_params.get('gender', None)

        cache_name_model = self.cache_name_prefix + (
            state + "_" if state is not None else "") + major + "_" + semester + "_" + gender + "_model"
        cache_name_serializer = self.cache_name_prefix + str(self.request.query_params['page']) + "_" + (
            state + "_" if state is not None else "") + major + "_" + semester + "_" + gender + "_serializer"

        applicants = self.get_applicants(self.get_applicants_queryset, cache_name_model, state, major, semester, gender)

        query = self.request.query_params.get('query')
        if query not in ["", None]:
            applicants = applicants.filter(
                Q(arabic_full_name__istartswith=query) | Q(full_name__istartswith=query) | Q(
                    national_id__istartswith=query) |
                Q(email__istartswith=query) | Q(arabic_last_name__icontains=query) | Q(last_name__icontains=query)
            ).order_by("-registration_date")

        if applicants is None or applicants.count() <= 0:
            return Response({"warning": "No applicants Found", "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        query = self.pagination_class.paginate_queryset(applicants, self.request)
        return self.pagination_class.get_paginated_response(
            self.get_data(EnglishCertificateListSerializer, query, cache_name=cache_name_serializer))

    def get_applicants_queryset(self, state, major, semester, gender):
        queryset = Applicant.objects.filter(
            english_certf_score__gt=0, apply_semester=semester,
        ).exclude(major_id__name='NM', english_certf_result__in=['F', 'L', 'U'])

        if state not in ['all', '', None]:
            if state == 'under':
                queryset = queryset.filter(english_certf_score__lt=40)
            else:
                queryset = queryset.filter(english_certf_result__exact=self.get_result_filter(state))
        if major not in ['all', '', None]:
            queryset = queryset.filter(major_id__name=major)
        if gender not in ['all', '', None]:
            queryset = queryset.filter(gender=gender)

        return queryset.order_by("-registration_date")

    @staticmethod
    def get_result_filter(state):
        result = {
            "not_graded": None,
            "succeed": "S",
        }
        return result.get(state, -1)

    @staticmethod
    def get_user(user_id):
        return User.objects.get(id=user_id)

    def get_applicants(self, function, cache_name, *args, **kwargs):
        if Signal.SIGNAL_APPLICANT:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_name_prefix))
            Signal.SIGNAL_APPLICANT = False

        return CacheModel(function=function, params=args, kwargs=kwargs, cache_name=cache_name).get_from_cache()

    @staticmethod
    def get_data(serializer_class, data, cache_name, many=True):
        return CacheSerializer(serializer=serializer_class, data=data, cache_name=cache_name,
                               many=many).get_from_cache()
