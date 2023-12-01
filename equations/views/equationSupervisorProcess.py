from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from email_handling.views.body_mails import studentEquationUpdateMail
from equations.models.courses import EquivalentCourse, UniversirtyCourse
from equations.models.equations import Equation
from equations.serializers.equationSerializer import ListEquationsSerializer, EditEquationSerializer
from equations.serializers.equivilantCoursesSerializer import ListEquivilantCoursesSerializer
from registration.models.applicant import Applicant
from registration.models.evaluation import EnglishTest
from registration.models.lookup import University
from registration.models.user_model import User
from registration.pagination.applicantListPagination import ApplicantListPagination
from registration.serializers.admin.admissionSerializer import EnglishRetreiveSerializer
from registration.tasks import send_email


class EquationSupervisorView(APIView):
    pagination_class = ApplicantListPagination()

    def get(self, request):

        # Current User
        currentUser = self.get_current_user(int(self.request.session['user']['pk']))
        if currentUser.role == 14:

            # Get one equation request
            applicant_id = self.request.query_params.get('applicant_id', None)
            if applicant_id:
                equ_request = self.get_one_equation(applicant_id)
                applicant_univ = self.get_applicant_univ(equ_request.applicant)
                applicant = self.get_applicant(applicant_id)
                eng = self.get_english_test(applicant_id)
                english_logs = {
                    "english_dates": None,
                    "certificate_data": None,
                }
                if eng.exists():
                    english_dates = EnglishRetreiveSerializer(eng, many=True).data
                    english_logs['english_dates'] = english_dates
                if self.check_english_certf(applicant):
                    english_certificate_data = {
                        "score": applicant.english_certf_score,
                        "confirmed": applicant.english_certf_confirmation,
                        "state": applicant.english_certf_result,
                        "university_certification": applicant.university_english_certification.url,
                    }
                    english_logs['certificate_data'] = english_certificate_data

                # Check if student has university
                if applicant_univ is None:
                    return Response({
                        "error": "No registered university for this student.",
                        "error_ar": "لا توجد جامعة مسجلة لهذا الطالب."
                    }, status=400)

                return Response(
                    {
                        "equation": ListEquationsSerializer(equ_request).data,
                        "equivalent_courses": ListEquivilantCoursesSerializer(
                            self.get_courses_per_univ(applicant_univ),
                            many=True).data,
                        "english_logs": english_logs,
                    }
                )
            # Filter equations
            state = self.request.query_params.get('state', None)
            confirmed = self.request.query_params.get('confirmed', None)
            if state and confirmed:
                pending_confirm = self.get_equations_filter_state_confirmed(
                    gender=self.request.query_params.get('gender', None),
                    semester=self.request.query_params.get('semester', None),
                    state=state,
                    confirmed=confirmed,
                    role=currentUser.user_major
                )
                query = self.request.query_params.get('query')
                if query not in ["", None]:
                    pending_confirm = pending_confirm.filter(
                        Q(applicant__arabic_full_name__istartswith=query)
                        | Q(applicant__national_id__istartswith=query)
                        | Q(applicant__full_name__istartswith=query)
                    ).order_by('-created')

                if not pending_confirm.exists():
                    return Response({"warning": "No equation requests found.", "warning_ar": "لا يوجد طلبات معادلة."},
                                    status=400)
                equations_pending_confirm_data_pagination = self.pagination_class.paginate_queryset(
                    pending_confirm,
                    self.request
                )
                return self.pagination_class.get_paginated_response(
                    ListEquationsSerializer(equations_pending_confirm_data_pagination, many=True).data)

            # Return all requests
            pending_equations = self.get_pending_equations(
                currentUser.gender,
                semester=self.request.query_params['semester'],
                role=currentUser.user_major
            )
            query = self.request.query_params.get('query')
            if query not in ["", None]:
                pending_equations = pending_equations.filter(
                    Q(applicant__arabic_full_name__istartswith=query)
                    | Q(applicant__national_id__istartswith=query)
                    | Q(applicant__full_name__istartswith=query)
                ).order_by('-created')

            if not pending_equations.exists():
                return Response({"warning": "No equation requests found.", "warning_ar": "لا يوجد طلبات معادلة."},
                                status=400)

            equations_data_pagination = self.pagination_class.paginate_queryset(
                pending_equations,
                self.request
            )
            return self.pagination_class.get_paginated_response(
                ListEquationsSerializer(equations_data_pagination, many=True).data)

        return Response({"error": "You don't have access.",
                         "error_ar": "ليس لديك صلاحية."}, status=400)

    @staticmethod
    def get_english_test(applicant_id):
        return EnglishTest.objects.filter(applicant_id_id=applicant_id).order_by('test_try')

    @staticmethod
    def check_english_certf(applicant):
        if isinstance(applicant.english_certf_score, float) and applicant.english_certf_score > 0:
            return True
        return False

    def put(self, request):
        if {"id"} <= self.request.data.keys():
            equation_request = self.get_one_equation(self.request.data['id'])
            applicant = self.get_applicant(equation_request.applicant.id)
            if equation_request:
                if 'exception' in self.request.data:
                    for i in self.request.data['exception']:
                        univ = self.get_univ_id(i['university'])
                        equ_to = self.get_univ_course(i['equivalent_to']['id'])
                        exception_course = EquivalentCourse.objects.filter(university=univ, equivalent_to=equ_to,
                                                                           code=i['code'], hours=i['hours'],
                                                                           exception=True)
                        if exception_course.exists():
                            self.request.data['equation_courses'].append(exception_course.last().id)
                        else:
                            exception_course = EquivalentCourse.objects.create(university=univ, equivalent_to=equ_to,
                                                                               code=i['code'],
                                                                               name=i['name'], hours=i['hours'],
                                                                               user=self.get_current_user(int(
                                                                                   self.request.session['user']['pk'])),
                                                                               exception=True)
                            self.request.data['equation_courses'].append(exception_course.id)
                eq_course = EditEquationSerializer(equation_request, data=self.request.data, partial=True)
                eq_course.is_valid(raise_exception=True)

                # Send email if rejected
                if eq_course.validated_data['init_state'] == 'RJ':
                    body = studentEquationUpdateMail()
                    send_email.delay(request.headers.get("origin"), applicant.first_name, applicant.email,
                                     english=body['english'], arabic=body['arabic'],
                                     subject='Al Maarefa University Equation Update',
                                     login="Login Now"
                                     )

                eq_course.save(user=self.get_current_user(self.request.session['user']['pk']))

                return Response({"success": "Equation Updated Successfully.",
                                 "success_ar": "تم تعديل طلب المعادلة بنجاح",
                                 "new_equation_request": ListEquationsSerializer(
                                     self.get_one_equation(applicant)).data})

            return Response({"error": "Equation request not found.",
                             "error_ar": "طلب المعادلة ليست متوفرة."}, status=400)

        return Response({"error": "Something went wrong.",
                         "error_ar": "حدث خطأ، الرجاء المحاولة مرة أخرى"}, status=400)

    def get_pending_equations(self, gender, semester, role):
        return Equation.objects.filter(applicant__gender=gender, applicant__apply_semester=semester,
                                       applicant__major_id__name=role).order_by('-created')

    @staticmethod
    def get_equations_filter_state_confirmed(gender, semester, role, state, confirmed):
        query = Equation.objects.filter(applicant__apply_semester=semester, applicant__major_id__name=role)

        if state not in ['all', '', None]:
            state = state.split('_')
            if state[0] == 'init':
                query = query.filter(init_state=state[-1].upper())
            elif state[0] == 'head_of_department':
                query = query.filter(head_of_department_state=state[-1].upper())
            else:
                query = query.filter(final_state=state[-1].upper())

        if confirmed not in ['all', '', None]:
            query = query.filter(confirmed=confirmed)

        if gender not in ['all', '', None]:
            query = query.filter(applicant__gender=gender)

        return query.order_by('-created')

    def get_one_equation(self, id):
        query = Equation.objects.filter(applicant=id)
        if query.exists():
            return query.last()
        return False

    def get_current_user(self, user_pk):
        return User.objects.get(pk=user_pk)

    def get_courses_per_univ(self, univ):
        university = University.objects.filter(
            Q(university_name_english__iregex=univ) | Q(university_name_arabic__iregex=univ)).last()
        if university:
            return EquivalentCourse.objects.filter(university=university.id, exception=False)
        return None

    def get_applicant(self, id):
        return Applicant.objects.get(id=id)

    def get_univ_id(self, name):
        return University.objects.filter(Q(university_name_english=name) | Q(university_name_arabic=name)).last()

    def get_univ_course(self, id):
        return UniversirtyCourse.objects.get(id=id)

    def get_applicant_univ(self, applicant):
        if applicant.previous_university:
            return applicant.previous_university
        return applicant.tagseer_institute
