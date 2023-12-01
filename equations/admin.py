from django.contrib import admin
from equations.models.courses import UniversirtyCourse, EquivalentCourse
from equations.models.equations import Equation
from equations.models.services import Service


class UniversityCourseAdmin(admin.ModelAdmin):
    search_fields = ('code', 'course_no', 'faculty',)
    list_display = ('name', 'course_no', 'arabic_name', 'code', 'hours', 'faculty')
    list_filter = ('faculty',)


class EquivalentCourseAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name', 'university__university_name_arabic', 'university__university_name_english',)
    list_display = ('name', 'university', 'code', 'hours', 'equivalent_to', 'exception',)
    list_filter = ('exception', 'university',)


class EquationAdmin(admin.ModelAdmin):
    search_fields = ('applicant__national_id', 'applicant__email', 'applicant__full_name',)
    filter_horizontal = ('equation_courses', )
    list_display = ('applicant', 'init_state', 'head_of_department_state', 'final_state', 'confirmed', 'comment')
    list_filter = ('init_state', 'head_of_department_state', 'final_state', 'confirmed')


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", 'active',)
    list_filter = ('name',)


admin.site.register(UniversirtyCourse, UniversityCourseAdmin)
admin.site.register(EquivalentCourse, EquivalentCourseAdmin)
admin.site.register(Equation, EquationAdmin)
admin.site.register(Service, ServiceAdmin)
