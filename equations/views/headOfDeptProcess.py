from rest_framework.views import APIView
from rest_framework.response import Response
from equations.serializers.equationSerializer import ListEquationsSerializer, HeadOfDeptEquationSerializer
from equations.models.equations import Equation
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.models.user_model import User
from django.db.models import Q
from email_handling.views.body_mails import studentEquationUpdateMail
from registration.tasks import send_email
from registration.models.applicant import Applicant


class HeadOfDeptEquationView(APIView):
    pagination_class = ApplicantListPagination()

    def get(self, request):
        current_user = self.get_current_user(int(self.request.session['user']['pk']))
        if current_user.role == 15:
            filter_params = {
                "semester": self.request.query_params['semester'],
                "major": None if current_user.user_major in ['M', 'PH', 'AS'] else current_user.user_major
            }

            # Filter equations based on state and confirmed with search
            if 'state' in self.request.query_params and 'confirmed' in self.request.query_params:
                filter_params.update(
                    {"state": self.request.query_params['state'], "confirmed": self.request.query_params['confirmed']})
                pending_confirm = self.get_equations_filter_state_confirmed(**filter_params)
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
                equ_request = self.get_one_equation(self.request.query_params['applicant_id'], current_user.user_major)
                if not equ_request:
                    return Response({"warning": "Equation not found or you dont have access.",
                                     "warning_ar": "لم يعثر على طلب المعادلة أو ليس لديك صلاحية."}, status=400)
                return Response({"equation": ListEquationsSerializer(equ_request).data})

            get_data = self.get_pending_equations(**filter_params)
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
        current_user = self.get_current_user(int(self.request.session['user']['pk']))
        if {"id"} <= self.request.data.keys() and current_user.role == 15:
            equation_request = self.get_one_equation(self.request.data['id'], current_user.user_major)
            if not equation_request:
                return Response({"warning": "Equation not found or you dont have access.",
                                 "warning_ar": "لم يعثر على طلب المعادلة أو ليس لديك صلاحية."}, status=400)
            applicant = self.get_applicant(equation_request.applicant.id)
            if equation_request:

                eq_course = HeadOfDeptEquationSerializer(equation_request, data=self.request.data, partial=True)
                eq_course.is_valid(raise_exception=True)

                # Send email if rejected or accepted
                if eq_course.validated_data.get('head_of_department_state') in ['RJ']:
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
                                     self.get_one_equation(applicant, current_user.user_major)).data})

            return Response({"error": "Equation request not found.",
                             "error_ar": "طلب المعادلة ليست متوفرة."}, status=400)

        return Response({"error": "Something went wrong.",
                         "error_ar": "حدث خطأ، الرجاء المحاولة مرة أخرى"}, status=400)

    def get_pending_equations(self, major, semester):
        return Equation.objects.filter(Q(init_state='AC') | Q(init_state='NM'), applicant__major_id__name=major,
                                       applicant__apply_semester=semester).order_by('-created')

    def get_equations_filter_state_confirmed(self, major, semester, state, confirmed):
        if state == 'all':
            if confirmed == 'all':
                return Equation.objects.filter(Q(init_state='AC') | Q(init_state='NM'), applicant__major_id__name=major,
                                               applicant__apply_semester=semester).order_by('-created')
            return Equation.objects.filter(Q(init_state='AC') | Q(init_state='NM'), applicant__major_id__name=major,
                                           applicant__apply_semester=semester, confirmed=confirmed).order_by('-created')
        else:
            state = state.split('_')
            if state[0] == 'init':
                if confirmed == 'all':
                    return Equation.objects.filter(applicant__apply_semester=semester, applicant__major_id__name=major,
                                                   init_state=state[-1].upper()).order_by('-created')
                return Equation.objects.filter(applicant__apply_semester=semester, applicant__major_id__name=major,
                                               init_state=state[-1].upper(), confirmed=confirmed).order_by('-created')
            elif state[0] == 'head_of_department':
                if confirmed == 'all':
                    return Equation.objects.filter(applicant__apply_semester=semester, applicant__major_id__name=major,
                                                   head_of_department_state=state[-1].upper()).order_by('-created')
                return Equation.objects.filter(applicant__apply_semester=semester, applicant__major_id__name=major,
                                               head_of_department_state=state[-1].upper(),
                                               confirmed=confirmed).order_by('-created')
            else:
                if confirmed == 'all':
                    return Equation.objects.filter(applicant__apply_semester=semester, applicant__major_id__name=major,
                                                   final_state=state[-1].upper()).order_by('-created')
                return Equation.objects.filter(applicant__apply_semester=semester, applicant__major_id__name=major,
                                               final_state=state[-1].upper(), confirmed=confirmed).order_by('-created')

    def get_one_equation(self, id, major):
        query = Equation.objects.filter(applicant=id)
        if query.exists() and query.last().applicant.major_id.name == major:
            return query.last()
        return None

    def get_current_user(self, user_pk):
        return User.objects.get(pk=user_pk)

    def get_applicant(self, id):
        return Applicant.objects.get(id=id)
