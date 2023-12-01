from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from registration.serializers.admin.deanEvalSerializer import InterviewRetrieveSerializer
from registration.models.evaluation import Interview
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination
from django.db.models import Q
from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.signals.interview import Signal


# Implemented By Mohamed Samy.


class DeanEval(GenericAPIView):
    pagination_class = ApplicantListPagination()
    cache_name_prefix = "dean_applicants_"

    def get(self, request, *args, **kwargs):
        if 'major' in self.request.query_params:

            user = self.get_queryset(int(self.request.session['user']['pk']))
            state = self.request.query_params.get('state', None)
            major = self.request.query_params.get('major', None)
            semester = self.request.query_params.get('semester', None)
            gender = self.request.query_params.get('gender', None)
            cache_name_model = self.cache_name_prefix + str(user.role) + "_" + (
                gender + "_" if gender is not None else "") + "_" + (
                                   state + "_" if state is not None else "") + major + "_" + semester + "_model"

            cache_name_serializer = self.cache_name_prefix + str(self.request.query_params['page']) + "_" + str(
                user.role) + "_" + (gender + "_" if gender is not None else "") + "_" + (
                                        state + "_" if state is not None else "") + major + "_" + semester + "_serializer"

            inter_applicant = self.get_applicants(self.get_applicants_from_role_user, cache_name_model, user.role,
                                                  state, gender, major, semester)

            query = self.request.query_params.get('query')
            if query not in ["", None]:
                inter_applicant = inter_applicant.filter(
                    Q(applicant_id__national_id__istartswith=query) | Q(applicant_id__last_name__icontains=query)
                    | Q(applicant_id__arabic_full_name__istartswith=query) | Q(applicant_id__email__istartswith=query)
                    | Q(applicant_id__full_name__istartswith=query) | Q(applicant_id__arabic_last_name__icontains=query)
                ).order_by("-reservation_id__reservation_date")

            if len(inter_applicant) <= 0:
                return Response({"warning": "No applicants Found", "warning_ar": "لا يوجد طلاب"},
                                status=HTTP_404_NOT_FOUND)

            applicant_page = self.pagination_class.paginate_queryset(inter_applicant, self.request)

            applicant = self.get_data(InterviewRetrieveSerializer, data=applicant_page,
                                      cache_name=cache_name_serializer, many=True)

            return self.pagination_class.get_paginated_response(applicant)
        else:
            return Response({"ERROR": "Sorry, Please Choose the correct major", "ERROR_ar": "برجاء اختيار تخصص صحيح"},
                            status=HTTP_404_NOT_FOUND)

    def get_queryset(self, user_id):
        return User.objects.get(id=user_id)

    def get_applicants_from_role_user(self, role, state, gender, major, semester):

        faculty = None
        if role == 7:
            faculty = "PH"
        elif role == 9:
            faculty = "M"
        elif role == 10:
            faculty = "AS"

        return self.get_applicants_filter(faculty, major, gender, state, semester)

    def get_applicants_filter(self, faculty, major, gender, state, semester):
        base_filter = Q(applicant_id__major_id__faculty_id__name__exact=faculty) & \
                      Q(applicant_id__major_id=major) & \
                      Q(applicant_id__apply_semester=semester)

        gender_filter = Q()
        if gender != 'all':
            gender_filter = Q(applicant_id__gender=gender)

        if state == 'fail':
            result_filter = Q(result='F')
        else:
            result_filter = Q(result='S')
            if state != 'all':
                final_state = self.get_final_state(state)
                result_filter &= Q(applicant_id__final_state__exact=final_state)

        return Interview.objects.filter(base_filter & gender_filter & result_filter).order_by(
            "-reservation_id__reservation_date")

    def get_final_state(self, state):
        f_state = {
            'accepted': "A",
            'rejected': "RJ",
            'waiting': "W",
            'rejected_major': "RJM",
            'not_reviewed': None
        }

        return f_state.get(state, -1)

    def get_applicants(self, function, cache_name, *args, **kwargs):
        if Signal.SIGNAL_INTERVIEW:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_name_prefix))
            Signal.SIGNAL_INTERVIEW = False

        return CacheModel(function=function, cache_name=cache_name, params=args, kwargs=kwargs).get_from_cache()

    def get_data(self, serializer_class, data, cache_name, many=True):
        return CacheSerializer(serializer=serializer_class,
                               data=data,
                               cache_name=cache_name,
                               many=many).get_from_cache()
