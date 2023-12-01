from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.response import Response

from registration.models.user_model import User
from registration.serializers.admin.admissionSerializer import UnregisteredApplicantListSerializer
from registration.models.applicant import Applicant
from registration.pagination.applicantListPagination import ApplicantListPagination
from django.db.models import Q
from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.signals.applicant import Signal


class UnregisteredApplicants(GenericAPIView):
    pagination_class = ApplicantListPagination()
    cache_name_prefix = "admission_applicants_unregistered_"

    def get(self, request, *args, **kwargs):
        major = request.query_params.get('major', None)
        gender = request.query_params.get('gender', None)
        semester = request.query_params.get('semester', None)
        contact_result = request.query_params.get('contact_result', None)
        cache_name_model = self.cache_name_prefix + gender + "_" + semester + "_model"
        cache_name_serializer = self.cache_name_prefix + str(self.request.query_params['page']) + "_" + gender + "_" + semester + "_serializer"

        applicants = self.get_applicants(
            self.get_applicant_data,
            cache_name_model,
            semester,
            contact_result,
            major
        )

        query = request.query_params.get('query')
        if query not in ["", None]:
            applicants = applicants.filter(
                Q(national_id__istartswith=query) | Q(arabic_full_name__istartswith=query) | Q(
                    full_name__istartswith=query) | Q(email__istartswith=query) |
                Q(arabic_last_name__icontains=query) | Q(last_name__icontains=query)).order_by("-registration_date")

        if applicants is None or applicants.count() <= 0:
            return Response({"warning": "No applicants Found", "warning_ar": "لا يوجد طلاب"}, status=HTTP_404_NOT_FOUND)

        return self.pagination_class.get_paginated_response(self.get_data(UnregisteredApplicantListSerializer,
                                                                          self.pagination_class.paginate_queryset(
                                                                              applicants, self.request),
                                                                          cache_name_serializer
                                                                          )
                                                            )

    def get_queryset(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_applicant_data(self, semester, contact_result, major):
        filter_params = {
            "init_state__isnull": True,
            "accepted_outside": False,
            "apply_semester": semester
        }

        if major not in ["", None, "all"]:
            filter_params["major_id__name"] = major

        if contact_result not in ["", None, "all"]:
            if contact_result == 'NC':
                filter_params["contacted"] = False
            else:
                filter_params["contact_result"] = contact_result

        return Applicant.objects.filter(**filter_params).order_by("-registration_date")

    def get_applicants(self, function, cache_name, *args, **kwargs):
        if Signal.SIGNAL_APPLICANT:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_name_prefix))
            Signal.SIGNAL_APPLICANT = False

        return CacheModel(function=function, params=args, kwargs=kwargs, cache_name=cache_name).get_from_cache()

    def get_data(self, serializer_class, data, cache_name, many=True):
        return CacheSerializer(serializer=serializer_class,
                               data=data,
                               cache_name=cache_name,
                               many=many).get_from_cache()
