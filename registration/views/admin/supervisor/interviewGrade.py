from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from registration.serializers.admin.interviewGradeSerializer import InterviewListSerializer
from registration.models.evaluation import Interview
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination
from django.db.models import Q
from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.signals.interview import Signal
from rest_framework.status import HTTP_403_FORBIDDEN


class InterviewGrade(GenericAPIView):
    pagination_class = ApplicantListPagination()
    cache_name_prefix = "interview_"

    def get(self, request, *args, **kwargs):
        currentUser = self.get_user(int(self.request.session['user']['pk']))
        userRole = currentUser.role
        faculty = currentUser.user_major if currentUser.user_major else 'all'
        if userRole in (2, 5,  6, 13, 90):
            # Params
            major = self.request.query_params.get('major', None)
            state = self.request.query_params.get('state', None)
            semester = self.request.query_params.get('semester', None)
            online = self.request.query_params.get('online', None)
            case = True if online in ("true", "True") else False
            gender = self.request.query_params.get('gender', None)

            cache_name_model = self.cache_name_prefix + (state + "_" if state is not None else "") + (major + "_" if major is not None else "") + semester + "_" + gender + "_model"

            cache_name_serializer = self.cache_name_prefix + str(self.request.query_params['page']) + "_" + (state + "_" if state is not None else "") + (major + "_" if major is not None else "") + semester + "_" + gender + "_serializer"

            interview = self.get_applicants(self.get_queryset, cache_name_model, state, faculty, major, semester, gender, case)

            query = self.request.query_params.get('query')
            if query not in ["", None]:
                interview = interview.filter(
                    Q(applicant_id__national_id__istartswith=query) | Q(applicant_id__email__istartswith=query) |
                    Q(applicant_id__arabic_full_name__istartswith=query) | Q(applicant_id__full_name__istartswith=query)
                    | Q(applicant_id__arabic_last_name__icontains=query) | Q(applicant_id__last_name__icontains=query)
                ).order_by("-reservation_id__reservation_date")

            if interview is None or interview.count() <= 0:
                return Response({"warning": "No applicants Found", "warning_ar": "لا يوجد طلاب"},
                                status=HTTP_404_NOT_FOUND)

            applicant_data_pagination = self.pagination_class.paginate_queryset(
                interview,
                self.request
            )
            applicants = self.get_data(serializer_class=InterviewListSerializer,
                                       data=applicant_data_pagination,
                                       cache_name=cache_name_serializer)

            return self.pagination_class.get_paginated_response(applicants)

        return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                        status=HTTP_403_FORBIDDEN)

    def get_queryset(self, state, faculty, major, semester, gender, case):
        search_fields = {} if faculty == 'all' else {
            'applicant_id__major_id__faculty_id__name' if faculty in ['M', 'PH', 'AS'] else 'applicant_id__major_id__name': faculty}

        if state in ['all', '', None] and major in ['all', '', None] and gender in ['all', '', None]:
            return Interview.objects.filter(**search_fields,
                                            applicant_id__apply_semester=semester,
                                            reservation_id__online=case
                                            ).order_by("-reservation_id__reservation_date")

        elif state in ['all', '', None] and major in ['all', '', None] and gender not in ['all', '', None]:
            return Interview.objects.filter(**search_fields, applicant_id__gender=gender,
                                            applicant_id__apply_semester=semester,
                                            reservation_id__online=case
                                            ).order_by("-reservation_id__reservation_date")

        elif state in ['all', '', None] and major not in ['all', '', None] and gender in ['all', '', None]:
            return Interview.objects.filter(applicant_id__major_id__name=major,
                                            applicant_id__apply_semester=semester,
                                            reservation_id__online=case
                                            ).order_by("-reservation_id__reservation_date")

        elif state in ['all', '', None] and major not in ['all', '', None] and gender not in ['all', '', None]:
            return Interview.objects.filter(applicant_id__gender=gender,
                                            applicant_id__major_id__name=major,
                                            applicant_id__apply_semester=semester,
                                            reservation_id__online=case
                                            ).order_by("-reservation_id__reservation_date")

        if state not in ['all', '', None] and major in ['all', '', None] and gender in ['all', '', None]:
            return Interview.objects.filter(**search_fields, esult__exact=self.get_result_filter(state),
                                            applicant_id__apply_semester=semester,
                                            reservation_id__online=case
                                            ).order_by("-reservation_id__reservation_date")

        elif state not in ['all', '', None] and major in ['all', '', None] and gender not in ['all', '', None]:
            return Interview.objects.filter(**search_fields, applicant_id__gender=gender,
                                            result__exact=self.get_result_filter(state),
                                            applicant_id__apply_semester=semester,
                                            reservation_id__online=case
                                            ).order_by("-reservation_id__reservation_date")

        elif state not in ['all', '', None] and major not in ['all', '', None] and gender in ['all', '', None]:
            return Interview.objects.filter(result__exact=self.get_result_filter(state),
                                            applicant_id__major_id__name=major,
                                            applicant_id__apply_semester=semester,
                                            reservation_id__online=case
                                            ).order_by("-reservation_id__reservation_date")

        return Interview.objects.filter(applicant_id__gender=gender,
                                        result__exact=self.get_result_filter(state),
                                        applicant_id__major_id__name=major,
                                        applicant_id__apply_semester=semester,
                                        reservation_id__online=case
                                        ).order_by("-reservation_id__reservation_date")

    def get_result_filter(self, state):
        result = {
            "not_graded": None,
            "succeed": "S",
            "failed": "F"
        }

        if state in result:
            return result[state]

        return -1

    def get_user(self, pk):
        return User.objects.get(id=pk)

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
