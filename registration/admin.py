from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.urls import path

from registration.models.chat import *
from registration.models.system_log import SystemLog
from registration.models.user_model import User
from registration.actions import importEregData
from registration.models.applicant import Applicant, Reservation, Payment, Files, Note, Certificate
from registration.models.evaluation import EnglishTest, Interview, Absent
from registration.models.lookup import University
from registration.models.oracle_process import OracleProcess, PaymentOracleProcess
from registration.models.sysadmin import UnivPayments, Role
from registration.models.univStructure import Faculty, Major

admin.site.site_header = "AlMaarefa University"


# Register your models here.

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin, importEregData):
    add_form = UserCreationForm
    model = User
    list_display = ('email', 'role', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active', 'role', 'signature',)
    filter_horizontal = ('user_roles',)
    # change_list_template = 'user/user.html'

    admin_for_add_users = 'admin@view.com'

    def get_queryset(self, request):
        user_perms = ['registration.add_user', 'registration.change_user',
                      'registration.delete_user', 'registration.view_user']

        if request.user.user_permissions.all().count() == 4 and request.user.has_perms(user_perms):
            self.admin_for_add_users = request.user.email
            if request.user.email == self.admin_for_add_users:
                return User.objects.exclude(is_staff=True)

        return User.objects.all()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.email if request.user.email == self.admin_for_add_users else None

        if is_superuser:
            form.base_fields['groups'].widget = forms.HiddenInput()
            form.base_fields['user_permissions'].widget = forms.HiddenInput()
            form.base_fields['is_staff'].widget = forms.HiddenInput()
            form.base_fields['role'].choices = (
                ('', '-----------'),
                (2, "Admission Department"),
                (3, "English Department"),
                (4, "Scholarships Department"),
                (5, "Supervisor Department"),
                (7, "Pharmacy Dean"),
                (9, "Medicine Dean"),
                (10, "Science Dean"),
                (11, "Register Review"),
                (12, "English Conformer"),
                (13, "Interview Test"),)

        return form

    fieldsets = (
        (None, {'fields': (
            'email', 'password', "userName", "role", "gender", 'Phone', 'full_name', 'signature', 'user_roles',
            'user_major')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        ('User Info', {
            'classes': ('wide',),
            'fields': ('full_name', 'email', 'password', 'userName', "role", "gender", 'Phone', 'user_major',)}
         ),
        ('User Permissions', {
            'classes': ('wide',),
            'fields': ('groups', 'user_permissions', 'is_staff', 'is_active')}
         ),
        ('Signature', {
            'classes': ('wide',),
            'fields': ('signature',)
        })
    )

    search_fields = ('email',)
    ordering = ('email',)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        additonal = [path('load/ereg/', self.refresh_ereg_data,
                          name='%s_%s_load_ereg_data' % info), ]
        urls = urls[:3] + additonal + urls[3:]

        return urls


class AddFileInline(admin.TabularInline):
    model = Files
    extra = 1


class ApplicantAdmin(admin.ModelAdmin):
    search_fields = ('id', 'national_id', 'email', 'full_name', 'application_no', 'arabic_full_name',)
    readonly_fields = ['password']
    list_display = (
        'full_name', 'email', 'national_id', 'apply_semester', 'init_state', 'final_state', 'registration_date',)
    list_display_links = ('full_name', 'email', 'national_id',)
    inlines = [AddFileInline]
    change_list_template = 'applicant/applicant.html'
    list_filter = (
        'gender', 'registration_date', 'apply_semester', 'init_state', 'final_state', 'offer', 'major_id',
        'applicant_type', 'nationality',
    )

    fieldsets = (
        ("Applicant Info", {
            "classes": "wide",
            "fields": ("application_no", "student_id", "modified_user"),
        }),
        ("Personal Info Arabic", {
            "classes": ("wide",),
            "fields": (
                "arabic_first_name", "arabic_middle_name", 'arabic_last_name', "arabic_full_name",
                "arabic_family_name"),
        }),
        ("Personal Info English", {
            "classes": ("wide", "collapse"),
            "fields": ("first_name", "middle_name", 'last_name',
                       "full_name", "family_name",
                       "email", 'national_id', "gender", "phone", "home_phone",
                       "birth_place", "birth_date", "birth_date_hegry",
                       "nationality", "mother_nationality", "marital_status"
                       ),
        }),
        ("Living Info", {
            "classes": ("wide", "collapse"),
            "fields": ("city", "building_no", "street_no", "district", "postal_code", "extra_code"),
        }),
        ("Health Info", {
            "classes": ("wide", "collapse"),
            "fields": ("health_state", "health_type"),
        }),
        ("Superior Info", {
            "classes": ("wide", "collapse"),
            "fields": (
                "superior_name", "superior_arabic_name", "superior_nationalID", "superior_qualification",
                "superior_relation", "superior_phone"),
        }),
        ("Emergency Info", {
            "classes": ("wide", "collapse"),
            "fields": ("emergency_name", "emergency_phone", "emergency_relation", "emergency_qualification",
                       "emergency_nationalID"),
        }),
        ("School Info", {
            "classes": ("wide", "collapse"),
            "fields": ("certificate_country", "high_school_city", "education_area",
                       "high_school_name", "high_school_year", "high_school_GPA",),
        }),
        ("Exam Info", {
            "classes": ("wide", "collapse"),
            "fields": ("qiyas_aptitude", "qiyas_achievement", 'sat_score', "secondary_type"),
        }),
        ("University Info", {
            "classes": ("wide", "collapse"),
            "fields": ("degree", "init_state", "init_state_date",
                       "final_state", "final_state_date", "registration_date", "apply_semester",
                       "last_semester", "major_id", "applicant_type", "accepted_outside", "certificate_status",
                       ),
        }),
        ("Periority Info", {
            "classes": ("wide", "collapse"),
            "fields": ("first_periority", "second_periority", "third_periority", "fourth_periority",
                       "fifth_periority", "sixth_periority", "seventh_periority",
                       "eighth_periority", "ninth_periority", "tenth_periority"),
        }),
        ("Applicant Tagseer Info", {
            "classes": ("wide", "collapse"),
            "fields": ("tagseer_country", "tagseer_institute",
                       "tagseer_department", "tagseer_GPA", "tagseer_year", "tagseer_number",
                       "tagseer_date"),
        }),

        ("Applicant Transferred Info", {
            "classes": ("wide", "collapse"),
            "fields": ("state_university", "previous_university", "previous_GPA",
                       "high_graduation_year", "max_gpa"),
        }),
        ("English Exam Info", {
            "classes": ("wide", "collapse"),
            "fields": ("english_grader", "english_certf_entry_user", "english_certf_score",
                       "english_certf_result", "modify_grader", "english_certf_confirmation",
                       "university_english_certification", "english_notes"),
        }),
        ("Equation Info", {
            "classes": ("wide", "collapse"),
            "fields": ("equation", "equation_fees_exempt",),
        }),
        ("Employer Info", {
            "classes": ("wide", "collapse"),
            "fields": ("employment_state", "employer",),
        }),
        ("Question Info", {
            "classes": ("wide", "collapse"),
            "fields": ("first_questionare", "second_questionare",),
        }),
        ("Condition & Offer Info", {
            "classes": ("wide", "collapse"),
            "fields": ("condition", "offer",),
        }),
        ("Contact Info", {
            "classes": ("wide", "collapse"),
            "fields": ("contacted", "contact_result",),
        }),
        ("Other Info", {
            "classes": ("wide", "collapse"),
            "fields": ("arabic_speaker", "notes", "pledge"),
        }),

    )

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        additional = [
            path('applicant/test/', self.change_users_to_test,
                 name='%s_%s_test' % info)
        ]
        urls = urls[:3] + additional + urls[3:]
        return urls

    def changelist_view(self, request, extra_context=None):
        if settings.MODE != 'production':
            extra = {'change_test': True}
        else:
            extra = {}
        extra.update(extra_context or {})
        return super(ApplicantAdmin, self).changelist_view(request, extra_context=extra)

    def change_users_to_test(self, request):
        if settings.MODE == 'production':
            self.message_user(request, "You can't do this action in the production!", messages.ERROR)
            return HttpResponseRedirect("../../")
        else:
            password = "django123"
            queryset = Applicant.objects.exclude(email__endswith='flycatch.com')

            if queryset:
                for applicant in queryset:
                    applicant.email = self.replace_domain(str(applicant.email))
                    applicant.password = make_password(password)
                    applicant.phone = "966554228858"
                    applicant.superior_phone = "966554228858"
                    applicant.save()

                self.message_user(
                    request, "Successfully Updated", messages.SUCCESS)
            else:
                self.message_user(
                    request, "No changed detected", messages.WARNING)

        return HttpResponseRedirect("../../")

    def replace_domain(self, email):
        parts = email.split('@')
        if len(parts) == 2:
            username, _ = parts
            new_email = f"{username}@flycatch.com"
            return new_email
        else:
            return email


class EnglishTestAdmin(admin.ModelAdmin):
    search_fields = ('applicant_id__national_id', 'applicant_id__email', 'applicant_id__full_name',)
    list_display = ('applicant_id', 'test_try', 'reservation_id', 'paid', 'result', 'confirmed',)
    list_filter = ('reservation_id__reservation_date', 'result', 'confirmed', 'applicant_id__apply_semester',)


class InterviewAdmin(admin.ModelAdmin):
    search_fields = ('applicant_id__national_id', 'applicant_id__email', 'applicant_id__full_name',)
    list_display = ('applicant_id', 'reservation_id', 'result',)
    list_filter = ('result', 'reservation_id__reservation_date', 'applicant_id__apply_semester',)


class UnivPaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_title", 'cost',)
    list_filter = ('payment_title',)


class FilesAdmin(admin.ModelAdmin):
    search_fields = ('applicant_id__national_id', 'applicant_id__email', 'applicant_id__full_name',)
    list_display = ("applicant_id", "file_name", "url", 'status',)
    list_filter = ("status", "file_name", "applicant_id__registration_date",)


class CertificateAdmin(admin.ModelAdmin):
    readonly_fields = ['created_date', 'modified_date']
    search_fields = ('applicant_id__national_id', 'applicant_id__email', 'applicant_id__full_name',)
    list_display = ['applicant', 'name', 'status', 'modified_date']
    list_filter = ['name', 'status', 'modified_date']


class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name",)


class MajorAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', "name",)
    list_filter = ('faculty_id', 'name',)


class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "test_type", "reservation_date", "capacity", "count", "gender", "start_time", "reserved", "user", 'faculty',)
    list_filter = ("reservation_date", "test_type", "gender", 'faculty', "reserved", 'start_time',)


class PaymentAdmin(admin.ModelAdmin):
    search_fields = ('applicant_id__national_id', 'applicant_id__email', 'applicant_id__full_name',)
    list_display = ("applicant_id", "payment_id", "payment_date", "by_cash", "paid",)
    list_filter = ("paid", "by_cash", "payment_date",)


class AbsentAdmin(admin.ModelAdmin):
    # resource_class = ReservationAdmin

    search_fields = ('applicant_id__national_id', 'applicant_id__email', 'applicant_id__full_name',)
    list_display = ("applicant_id", "reservation_date", "test_type",)

    def reservation_date(self, obj):
        return Reservation.objects.get(pk=obj.reservation_id.id).reservation_date

    def test_type(self, obj):
        return Reservation.objects.get(pk=obj.reservation_id.id).test_type


class RolesAdmin(admin.ModelAdmin):
    list_display = ("role",)


class OracleProcessAdmin(admin.ModelAdmin):
    list_display = ("email", "national_id", 'created', 'process', 'send', 'delivered', 'number_tries')
    search_fields = ('email', 'national_id',)
    list_filter = ('process', "send", 'delivered', 'number_tries')


class PaymentOracleProcessAdmin(admin.ModelAdmin):
    list_display = ("email", "national_id", 'created', 'process', 'send', 'delivered', 'number_tries')
    search_fields = ('email', 'national_id',)
    list_filter = ('process', "send", 'delivered', 'number_tries')


class CountryAdmin(admin.ModelAdmin):
    list_display = ["country_no", "country_name_english", "country_name_arabic", "category_code"]


class CityAdmin(admin.ModelAdmin):
    list_display = ["city_no", "city_name_english", "city_name_arabic", "country_no"]


class ZoneAdmin(admin.ModelAdmin):
    list_display = ["zone_no", "zone_name_english", "zone_name_arabic", "city_no", "country_no"]


class SchoolAdmin(admin.ModelAdmin):
    list_display = ["school_no", "school_name_english", "school_name_arabic", "school_type", "zone", "city_no",
                    "country_no"]


admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, RolesAdmin)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Files, FilesAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(Note)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(EnglishTest, EnglishTestAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(University)
admin.site.register(Absent, AbsentAdmin)

# payment services
admin.site.register(UnivPayments, UnivPaymentAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OracleProcess, OracleProcessAdmin)
admin.site.register(PaymentOracleProcess, PaymentOracleProcessAdmin)
admin.site.register(SystemLog)

# chat models
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Participants)
admin.site.register(ConversationParticipants)
admin.site.register(MessageParticipants)
