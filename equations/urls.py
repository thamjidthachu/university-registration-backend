from unicodedata import name
from django.urls import path, include
from equations.views.getCourses import GetUniversityCourses
from equations.views.addEquivilantCourses import EquivilantCoursesView
from equations.views.studentEquationRequest import StudentEquationView
from equations.views.equationSupervisorProcess import EquationSupervisorView
from equations.views.deanEquationProcess import DeanEquationsView
from registration.views.admin.admission.serviceManagement import ServiceManagement
from equations.views.admissionEquations import EquationAdmissionView
from equations.views.studentCoursesPerUniv import StudentCoursesView
from equations.views.reports.equationReport import EquationsReport
from equations.views.updateEquationFile import UpdateEquationFile
from equations.views.headOfDeptProcess import HeadOfDeptEquationView

app_name = 'equations'

urlpatterns = [
    # load mcst courses
    path('equations/eregister/getcourses', GetUniversityCourses.as_view(), name='getcourses'),

    # List all equivalent courses to student for his university only
    path('equations/student/list', StudentCoursesView.as_view(), name='equatios-list-courses'),

    # List all equivalent courses and add new (Admission manager and equation supervisor only)
    path('equations', EquivilantCoursesView.as_view(), name='equations-list-add'),

    # List Equations and Create for Applicant
    path('equations/student', StudentEquationView.as_view(), name='equations-list-create-student'),

    # List Equation views and edit and delete them (Equation Supervisor Only)
    path('equations/supervisor', EquationSupervisorView.as_view(), name='equations-list-edit-supervisor'),

    # List Equation according to Dean's faculty and edit them
    path('equations/dean', DeanEquationsView.as_view(), name='equations-list-edit-dean'),

    # admission manager View
    path('equations/admission', EquationAdmissionView.as_view(), name='admission-equations'),

    # List all Services in order to manage its status 
    path('equations/service/status', ServiceManagement.as_view(), name='service_management'),

    # Reports
    path('equations/reports/all', EquationsReport.as_view(), name='equations-report'),

    # Update equation file
    path('equations/file/<int:pk>', UpdateEquationFile.as_view(), name='update-file'),

    # Head of department
    path('equations/hod', HeadOfDeptEquationView.as_view(), name='head-of-department'),

]
