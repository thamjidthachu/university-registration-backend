from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from equations.models.courses import EquivalentCourse
from equations.models.courses import UniversirtyCourse
from equations.serializers.equivilantCoursesSerializer import ListEquivilantCoursesSerializer, \
    CreatequivilantCoursesSerializer
from equations.serializers.universityCoursesSerializer import UniversityCourseDetailSerializer
from registration.models.lookup import University
from registration.models.user_model import User


class EquivilantCoursesView(APIView):

    def get(self, request):
        if User.objects.get(pk=int(self.request.session['user']['pk'])).role in [6, 14]:
            all_courses = self.get_courses()
            if len(all_courses) == 0:
                return Response({"warning": "No courses found", "warning_ar": "لا يوجد مواد معادلة.",
                                 'courses': UniversityCourseDetailSerializer(UniversirtyCourse.objects.all(),
                                                                             many=True).data}, status=400)

            return Response({'equivilant_courses': ListEquivilantCoursesSerializer(self.get_courses(), many=True).data,
                             'courses': UniversityCourseDetailSerializer(UniversirtyCourse.objects.all(),
                                                                         many=True).data})

        return Response({"error": "You don't have access.",
                         "error_ar": "ليس لديك صلاحية."}, status=400)

    def post(self, request):
        if {"university", "equivalent_to"} <= self.request.data.keys():
            # self.request.data._mutable = True
            # Change User Status to current user
            self.request.data['user'] = self.request.session['user']['pk']
            # Get university ID
            univ_instance = self.get_univ_id(self.request.data['university'])

            if not univ_instance:
                return Response({"error": "Error in student university",
                                 "error_ar": "خطأ في جامعة الطالب"}, status=400)

            self.request.data['university'] = univ_instance
            eq_course = CreatequivilantCoursesSerializer(data=self.request.data)
            eq_course.is_valid(raise_exception=True)
            eq_course.save()

            return Response({"success": "Course added successfully.",
                             "success_ar": "تم اضافة المقرر بنجاح",
                             "new_equivilant": ListEquivilantCoursesSerializer(
                                 self.get_one_equivilant_course(eq_course.data['id'])).data})

        return Response({"error": "Something went wrong.",
                         "error_ar": "حدث خطأ، الرجاء المحاولة مرة أخرى"}, status=400)

    def put(self, request):
        if {"id"} <= self.request.data.keys():
            equivilant_course = self.get_one_equivilant_course(self.request.data['id'])
            if equivilant_course:
                # self.request.data._mutable = True
                self.request.data['user'] = self.request.session['user']['pk']
                univ_instance = self.get_univ_id(self.request.data['university'])

                if not univ_instance:
                    return Response({"error": "Error in student university",
                                     "error_ar": "خطأ في جامعة الطالب"}, status=400)

                self.request.data['university'] = univ_instance
                eq_course = CreatequivilantCoursesSerializer(equivilant_course, data=self.request.data, partial=True)
                eq_course.is_valid(raise_exception=True)
                eq_course.save()

                return Response({"success": "Course Updated Successfully.",
                                 "success_ar": "تم تعديل المقرر بنجاح",
                                 "new_equivilant": ListEquivilantCoursesSerializer(
                                     self.get_one_equivilant_course(self.request.data['id'])).data})

            return Response({"error": "Course not found.",
                             "error_ar": "المقرر غير متوفر."}, status=400)

        return Response({"error": "Something went wrong.",
                         "error_ar": "حدث خطأ، الرجاء المحاولة مرة أخرى"}, status=400)

    def delete(self, request):
        if {"id"} <= self.request.data.keys():
            query = self.get_one_equivilant_course(self.request.data['id'])
            if query:
                query.delete()
                resp = Response({"success": "Course Deleted Successfully.",
                                 "success_ar": "تم حذف المقرر بنجاح."})
                resp['Access-Control-Allow-Origin'] = '*'
                return resp

            return Response({"error": "Course doesn\'t exist.",
                             "error_ar": "المقرر غير متواجد."}, status=400)

        return Response({"error": "Something went wrong.",
                         "error_ar": "حدث خطأ، الرجاء المحاولة مرة أخرى"}, status=400)

    def get_courses(self):
        return EquivalentCourse.objects.filter(exception=False)

    def get_one_equivilant_course(self, id):
        try:
            query = EquivalentCourse.objects.get(id=id)
            return query
        except:
            return False

    def get_univ_id(self, name):
        result = University.objects.filter(
            Q(university_name_english__iregex=name) | Q(university_name_arabic__iregex=name)).last()
        if result:
            return result.id
        return None
