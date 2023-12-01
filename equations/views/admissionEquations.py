from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from equations.models.equations import Equation
from equations.serializers.equationSerializer import ListEquationsSerializer
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination


class EquationAdmissionView(APIView):
    pagination_class = ApplicantListPagination()

    def get(self, request):

        if self.get_current_user(int(self.request.session['user']['pk'])).role == 6:
            applicant_id = self.request.query_params.get('applicant_id', None)

            # Get one equation request
            if applicant_id:
                equ_request = self.get_one_equation(applicant_id)
                return Response({"equation": ListEquationsSerializer(equ_request).data})

            # Params
            major = self.request.query_params.get('major', None)
            confirmed = self.request.query_params.get('confirmed', None)
            semester = self.request.query_params.get('semester', None)
            gender = self.request.query_params.get('gender', None)

            # Return all requests
            pending_equations = self.get_equations_filter(
                gender=gender,
                semester=semester,
                major=major,
                confirmed=confirmed
            )

            query = self.request.query_params.get('query')
            if query not in ["", None]:
                pending_equations = pending_equations.filter(
                    Q(applicant__arabic_full_name__istartswith=query) |
                    Q(applicant__national_id__startswith=query) |
                    Q(applicant__full_name__istartswith=query)
                ).order_by('-created')

            if not pending_equations.exists():
                return Response(
                    {"warning": "No equation requests found.", "warning_ar": "لا يوجد طلبات معادلة."}, status=400
                )

            equations_data_pagination = self.pagination_class.paginate_queryset(
                pending_equations,
                self.request
            )
            return self.pagination_class.get_paginated_response(
                ListEquationsSerializer(equations_data_pagination, many=True).data)

        return Response(
            {"error": "You don't have access.", "error_ar": "ليس لديك صلاحية."}, status=400
        )

    @staticmethod
    def get_equations_filter(semester, major, gender, confirmed):
        filters = {
            'applicant__apply_semester': semester,
        }

        if major not in ['all', '', None]:
            filters['applicant__major_id__name'] = major

        if gender not in ['all', '', None]:
            filters['applicant__gender'] = gender

        if confirmed not in ['all', '', None]:
            filters['confirmed'] = confirmed

        return Equation.objects.filter(**filters).order_by('-created')

    @staticmethod
    def get_one_equation(applicant_id):
        query = Equation.objects.filter(applicant=applicant_id)
        if query.exists():
            return query.last()
        return False

    @staticmethod
    def get_current_user(user_id):
        return User.objects.get(pk=user_id)
