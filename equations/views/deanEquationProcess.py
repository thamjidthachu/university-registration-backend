from rest_framework.views import APIView
from rest_framework.response import Response
from equations.serializers.equationSerializer import ListEquationsSerializer, EditEquationSerializer, \
    DeanEditEquationSerializer
from rest_framework.permissions import IsAuthenticated
from equations.models.equations import Equation
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.models.user_model import User
from django.db.models import Q
from email_handling.views.body_mails import studentEquationUpdateMail
from registration.tasks import send_email
from registration.models.applicant import Applicant


class DeanEquationsView(APIView):
    pagination_class = ApplicantListPagination()

    dean_faculty = {7: "PH",  # pharmacy
                    9: "M",  # Medicine
                    10: "AS",  # Science
                    }

    def get(self, request):
        current_role = self.get_current_user(int(self.request.session['user']['pk'])).role
        if current_role in [7, 9, 10]:

            # Filter equations based on state and major and confirmed with search
            if 'major' in self.request.query_params and 'state' in self.request.query_params and 'confirmed' in self.request.query_params:
                pending_confirm = self.get_equations_filter_state_major_confirmed(dean_fac=current_role,
                                                                                  semester=self.request.query_params[
                                                                                      'semester'],
                                                                                  state=self.request.query_params[
                                                                                      'state'],
                                                                                  major=self.request.query_params[
                                                                                      'major'],
                                                                                  confirmed=self.request.query_params[
                                                                                      'confirmed'])
                query = self.request.query_params.get('query')
                if query not in ["", None]:
                    pending_confirm = pending_confirm.filter(Q(applicant__arabic_full_name__istartswith=query) | Q(
                        applicant__national_id__istartswith=query)).order_by('-created')
                if not pending_confirm.exists():
                    return Response({"warning": "No equation requests found.", "warning_ar": "لا يوجد طلبات معادلة."},
                                    status=400)
                equations_pending_confirm_data_pagination = self.pagination_class.paginate_queryset(
                    pending_confirm,
                    self.request
                )
                return self.pagination_class.get_paginated_response(
                    ListEquationsSerializer(equations_pending_confirm_data_pagination, many=True).data)

            # Return one equation request
            if 'applicant_id' in self.request.query_params:
                equ_request = self.get_one_equation(self.request.query_params['applicant_id'])
                return Response({"equation": ListEquationsSerializer(equ_request).data})

            # Return equations related to the dean's faculty
            get_data = self.get_pending_equations_for_faculty(current_role,
                                                              semester=self.request.query_params['semester'])
            query = self.request.query_params.get('query')
            if query not in ["", None]:
                get_data = get_data.filter(Q(applicant__arabic_full_name__icontains=query) | Q(
                    applicant__national_id__contains=query)).order_by('-created')

            if not get_data.exists():
                return Response({"warning": "No equation requests found.", "warning_ar": "لا يوجد طلبات معادلة."},
                                status=400)

            equations_data_pagination = self.pagination_class.paginate_queryset(
                get_data,
                self.request
            )

            return self.pagination_class.get_paginated_response(
                ListEquationsSerializer(equations_data_pagination, many=True).data)

        return Response({"error": "You don't have access.", "error_ar": "ليس لديك صلاحية."}, status=400)

    def put(self, request):
        if {"id"} <= self.request.data.keys():
            equation_request = self.get_one_equation(self.request.data['id'])
            applicant = self.get_applicant(equation_request.applicant.id)
            if equation_request:

                eq_course = DeanEditEquationSerializer(equation_request, data=self.request.data, partial=True)
                eq_course.is_valid(raise_exception=True)

                # Send email if rejected or accepted
                if eq_course.validated_data['final_state'] in ['RJ', 'AC']:
                    body = studentEquationUpdateMail()
                    send_email.delay(request.headers.get("origin"), applicant.first_name, applicant.email,
                                     english=body['english'], arabic=body['arabic'],
                                     subject='Al Maarefa University Equation Update',
                                     login="Login Now"
                                     )

                eq_course.update(equation_request, eq_course.validated_data)
                return Response({"success": "Equation Updated Successfully.",
                                 "success_ar": "تم تعديل طلب المعادلة بنجاح",
                                 "new_equation_request": ListEquationsSerializer(
                                     self.get_one_equation(applicant)).data})

            return Response({"error": "Equation request not found.",
                             "error_ar": "طلب المعادلة ليست متوفرة."}, status=400)

        return Response({"error": "Something went wrong.",
                         "error_ar": "حدث خطأ، الرجاء المحاولة مرة أخرى"}, status=400)

    def get_pending_equations_for_faculty(self, dean_fac, semester):
        return Equation.objects.filter(Q(head_of_department_state='AC') | Q(init_state='NM'),
                                       applicant__major_id__faculty_id__name=self.dean_faculty[dean_fac],
                                       applicant__apply_semester=semester).order_by('-created')

    def get_equations_filter_state_major_confirmed(self, dean_fac, semester, state, major, confirmed):
        base_query = Equation.objects.filter(Q(head_of_department_state='AC') | Q(init_state='NM'),
                                             applicant__apply_semester=semester)

        if major != 'all':
            base_query = base_query.filter(applicant__major_id__name=major)

        if state != 'all':
            state = state.split('_')
            if state[0] == 'init':
                base_query = base_query.filter(init_state=state[-1].upper())
            elif state[0] == 'final':
                base_query = base_query.filter(final_state=state[-1].upper())
            else:
                base_query = base_query.filter(head_of_department_state=state[-1].upper())

        if confirmed != 'all':
            base_query = base_query.filter(confirmed=confirmed)

        if dean_fac != 'all':
            base_query = base_query.filter(applicant__major_id__faculty_id__name=self.dean_faculty[dean_fac])

        return base_query.order_by('-created')

    def get_one_equation(self, id):
        query = Equation.objects.filter(applicant=id)
        if query.exists():
            return query.last()
        return False

    def get_current_user(self, user_pk):
        return User.objects.get(pk=user_pk)

    def get_applicant(self, id):
        return Applicant.objects.get(id=id)
