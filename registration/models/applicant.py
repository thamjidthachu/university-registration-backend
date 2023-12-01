from django.db import models
from django.utils.timezone import now
from django.template.defaultfilters import slugify
from .user_model import User
from .univStructure import Major
from .sysadmin import UnivPayments
from django.conf import settings


# Create your models here.
QUALIFICATION_CHOICES = (
    ('UE', 'Uneducated'),
    ('EL', 'Elementary'),
    ('INT', 'Intermediate'),
    ('HS', 'High school'),
    ('DP', 'Diploma'),
    ('UG', 'Bachelors'),
    ('PG', 'Masters'),
    ('DR', 'Doctors'),
)

CERTIFICATE_CHOICES = (
    ('HS', 'High School Certificate'),
    ('AC', 'Certified Academic Record'),
    ('BDC', 'Bachelor Degree Certificate'),
    ('DC', 'Diploma Certificate'),
    ('IC', 'Certificate of Completion Internship')
)

CONTACT_RESULTS = (
    ('WA', 'Will Attend'),
    ('NR', 'No Reply'),
    ('WR', 'Withdrew Registration'),
    ('MM', 'Major Medicine'),
    ('NT', 'Need Time'),
    ('UP', 'Uploading Process')

)
CERTIFICATE_STATUS_CHOICES = (
    ('NS', 'Not Submitted'),
    ('PS', 'Partially Submitted'),
    ('FS', 'Fully Submitted'),
)
DEGREE_CHOICES = (
    ('UG', 'Bachelors'),
    ('PG', 'Masters'),
)

INIT_STAT_CHOICES = (
    ('UR', 'Under Review'),
    ('IA', 'Initial Acceptance'),
    ('CA', 'Conditional Acceptance'),
    ('RJ', 'Rejected'),
    ('WR', 'Withdrew Registration'),
)
FINAL_STAT_CHOICES = (
    ('A', 'Accepted'),
    ('RJ', 'Rejected'),
    ('RJM', 'Rejected In Major'),
    ('W', 'Put On waiting'),
)
GENDER_CHOICES = (
    ('F', 'Female'),
    ('M', 'Male'),
)
EVAL_CHOICES = (
    ('S', 'Succeeded'),
    ('F', 'Failed'),
    ('L', 'Low Score'),
    ('U', 'Unknown Certificate'),
)
APPLY_CHOICES = (
    ('FS', 'Fresh Student'),
    ('TS', 'Transferred Student'),
    ('HD', 'Health Diploma Student'),
)
OFFER_CHOICES = (
    ("AC", "Accepted"),
    ("RJ", "Rejected"),
)
FILE_STAT_CHOICES = (
    ('A', 'Accepted'),
    ('RJ', 'Rejected'),
)

STATE_UNIVERSITY_CHOICES = (
    ('RE', 'Regular'),
    ('OU', 'Outgoing'),
    ('AP', 'Apologize'),
    ('PP', 'Postponed'),
    ('AS', 'Academically_separated'),
    ('DD', 'Disciplinary_disconnected'),
    ('FR', 'Folded_registration'),
    ('GR', 'Graduated'),
)
MARITAL_STATUS_CHOICES = (
    (1, "Single"),
    (2, "Married"),
    (3, "Divorced"),
    (4, "Widowed")
)

EMPLOYER_CHOICES = (
    (1, "Government"),
    (2, "Private"),
)


def get_image_filename(instance, filename):
    slug = slugify(instance.applicant_id.application_no)
    return "applicant_%s/%s" % (slug, filename)


def get_filename(instance, filename):
    slug = slugify(instance.application_no)
    return "applicant_%s/%s" % (slug, filename)


class Applicant(models.Model):
    application_no = models.IntegerField(unique=True)
    modified_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="modify_applicant")

    ''' names Data '''
    first_name = models.CharField(max_length=500)
    middle_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    family_name = models.CharField(max_length=500)
    full_name = models.CharField(max_length=2500)
    arabic_first_name = models.CharField(max_length=500)
    arabic_middle_name = models.CharField(max_length=500)
    arabic_last_name = models.CharField(max_length=500)
    arabic_family_name = models.CharField(max_length=500)
    arabic_full_name = models.CharField(max_length=2500)

    ''' superior Data'''
    superior_name = models.CharField(max_length=100)
    superior_arabic_name = models.CharField(max_length=100, blank=True, null=True)
    superior_nationalID = models.CharField(max_length=100)
    superior_relation = models.CharField(max_length=100)
    superior_qualification = models.CharField(choices=QUALIFICATION_CHOICES, default='UE', max_length=20)
    superior_phone = models.CharField(max_length=100)

    ''' emergency Data'''
    emergency_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_relation = models.CharField(max_length=20, blank=True, null=True)
    emergency_nationalID = models.CharField(max_length=100, blank=True, null=True)
    emergency_qualification = models.CharField(choices=QUALIFICATION_CHOICES, default='UE', max_length=20)

    ''' Personal Data'''
    home_phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField('Password', max_length=128, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    birth_place = models.CharField(max_length=50)
    birth_date = models.DateField(max_length=20, blank=True, null=True)
    birth_date_hegry = models.CharField(max_length=10, blank=True, null=True)
    employment_state = models.CharField(max_length=50)
    employer = models.SmallIntegerField(choices=EMPLOYER_CHOICES, null=True, blank=True)
    first_questionare = models.CharField(max_length=10)
    second_questionare = models.CharField(max_length=10)

    ''' Living Data'''
    city = models.CharField(max_length=30, blank=True, null=True)
    building_no = models.CharField(max_length=20, blank=True, null=True)
    street_no = models.CharField(max_length=20, blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    extra_code = models.CharField(max_length=20, blank=True, null=True)

    ''' School Data'''
    certificate_country = models.CharField(max_length=50)
    education_area = models.CharField(max_length=50, blank=True, null=True)
    high_school_city = models.CharField(max_length=30, blank=True, null=True)
    high_school_GPA = models.FloatField(blank=True, null=True)
    high_school_year = models.IntegerField(blank=True, null=True)
    equation = models.FloatField(blank=True, null=True)
    high_school_name = models.CharField(max_length=500, blank=True, null=True)

    '''Achievements'''
    qiyas_aptitude = models.FloatField(blank=True, null=True)
    qiyas_achievement = models.FloatField(blank=True, null=True)
    sat_score = models.FloatField(blank=True, null=True)
    secondary_type = models.CharField(max_length=20)

    ''' Tagseer Data'''
    tagseer_institute = models.CharField(max_length=500, blank=True, null=True)
    tagseer_department = models.SmallIntegerField(blank=True, null=True)
    tagseer_GPA = models.FloatField(blank=True, null=True)
    tagseer_year = models.CharField(max_length=50, blank=True, null=True)
    tagseer_number = models.CharField(max_length=500, blank=True, null=True)
    tagseer_date = models.DateField(blank=True, null=True)
    tagseer_country = models.CharField(max_length=50, blank=True, null=True)

    ''' Health Data'''
    health_state = models.CharField(max_length=50)
    health_type = models.CharField(max_length=50, blank=True, null=True)

    ''' Al-Maarefa University Data'''
    degree = models.CharField(choices=DEGREE_CHOICES, default='UG', max_length=50)
    init_state = models.CharField(choices=INIT_STAT_CHOICES, blank=True, null=True, max_length=50)
    final_state = models.CharField(choices=FINAL_STAT_CHOICES, blank=True, null=True, max_length=50)
    init_state_date = models.DateTimeField(blank=True, null=True)
    final_state_date = models.DateTimeField(blank=True, null=True)
    registration_date = models.DateTimeField(default=now)
    major_id = models.ForeignKey(Major, blank=True, null=True, on_delete=models.CASCADE)
    apply_semester = models.CharField(max_length=50, blank=True, null=True)
    last_semester = models.CharField(max_length=50, blank=True, null=True)
    applicant_type = models.CharField(choices=APPLY_CHOICES, blank=True, null=True, max_length=50)
    condition = models.TextField(max_length=1000, blank=True, null=True)
    offer = models.CharField(max_length=10, choices=OFFER_CHOICES, blank=True, null=True)
    contacted = models.BooleanField(default=False)
    contact_result = models.CharField(choices=CONTACT_RESULTS, blank=True, null=True, max_length=10)
    accepted_outside = models.BooleanField(default=False)
    notes = models.TextField(max_length=1000, blank=True, null=True)
    english_notes = models.TextField(max_length=1000, blank=True, null=True)
    pledge = models.BooleanField(blank=True, null=True)
    certificate_status = models.CharField(choices=CERTIFICATE_STATUS_CHOICES, blank=True, null=True, max_length=10)

    ''' Transferred Applicant University Data'''
    high_graduation_year = models.IntegerField(blank=True, null=True)
    previous_GPA = models.FloatField(blank=True, null=True)
    previous_university = models.CharField(max_length=500, blank=True, null=True)
    max_gpa = models.FloatField(blank=True, null=True)
    state_university = models.CharField(max_length=10, choices=STATE_UNIVERSITY_CHOICES, blank=True, null=True)

    ''' English Data'''
    english_grader = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    english_certf_entry_user = models.CharField(max_length=100, blank=True, null=True)
    english_certf_score = models.FloatField(default=0)
    english_certf_result = models.CharField(choices=EVAL_CHOICES, max_length=3, blank=True, null=True)
    modify_grader = models.DateTimeField(blank=True, null=True)
    english_certf_confirmation = models.BooleanField(default=False)
    university_english_certification = models.FileField(upload_to=get_filename, blank=True, null=True)

    '''Nationality Data'''
    nationality = models.CharField(max_length=20)
    mother_nationality = models.CharField(max_length=50)
    national_id = models.CharField(max_length=100)
    arabic_speaker = models.BooleanField(default=False)

    '''Priorities Data'''
    first_periority = models.IntegerField(blank=True, null=True)
    second_periority = models.IntegerField(blank=True, null=True)
    third_periority = models.IntegerField(blank=True, null=True)
    fourth_periority = models.IntegerField(blank=True, null=True)
    fifth_periority = models.IntegerField(blank=True, null=True)
    sixth_periority = models.IntegerField(blank=True, null=True)
    seventh_periority = models.IntegerField(blank=True, null=True)
    eighth_periority = models.IntegerField(blank=True, null=True)
    ninth_periority = models.IntegerField(blank=True, null=True)
    tenth_periority = models.IntegerField(blank=True, null=True)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    marital_status = models.SmallIntegerField(choices=MARITAL_STATUS_CHOICES, blank=True, null=True)

    '''Equations'''
    equation_fees_exempt = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Note(models.Model):
    modified_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="note_user")
    applicant_name = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="note_applicant")
    note = models.TextField(max_length=1000, blank=True, null=True)
    created = models.DateTimeField(default=now)

    def __str__(self):
        return self.applicant_name.full_name


class Certificate(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="certificate_applicant")
    name = models.CharField(choices=CERTIFICATE_CHOICES, max_length=100, null=True, blank=True)
    approve_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approve_user", null=True, blank=True)
    status = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.applicant.full_name


class Files(models.Model):
    applicant_id = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="applicants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    modify_user = models.DateTimeField(blank=True, null=True)
    file_name = models.CharField(max_length=50)
    url = models.FileField(upload_to=get_image_filename)
    status = models.CharField(choices=FILE_STAT_CHOICES, blank=True, null=True, max_length=10)
    rej_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"

    def __str__(self):
        return self.applicant_id.full_name


class Reservation(models.Model):
    Type = (
        ("1", "English"),
        ("2", "Interview"),
    )
    Gender = (
        ("M", "Male"),
        ("F", "Female"),
    )
    FACULTY_CHOICES = (
        ("M", "Medicine"),
        ("PH", "Pharmacy"),
        ("AS", "Applied Science"),
        ("ALL", "All Faculties"),
    )
    test_type = models.CharField(max_length=1, choices=Type)
    faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES, default='ALL')
    capacity = models.IntegerField(default=1)
    gender = models.CharField(max_length=2, choices=Gender, null=True, blank=True)
    count = models.IntegerField(default=0)
    reservation_date = models.DateField()
    start_time = models.TimeField()
    duration_time = models.FloatField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    online = models.BooleanField(default=True)
    reserved = models.BooleanField(default=False)

    class Meta:
        ordering = ("-reservation_date",)

    def __str__(self):
        return dict(self.Type)[self.test_type] + " " + str(self.reservation_date)


class Payment(models.Model):
    payment_id = models.ForeignKey(UnivPayments, related_name='pay_amount', on_delete=models.CASCADE)
    applicant_id = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    by_cash = models.BooleanField(default=False)
    checkout_id = models.CharField(max_length=300)
    entity_id = models.CharField(max_length=300, blank=True, null=True)
    payment_date = models.DateTimeField(default=now)
    transaction_id = models.CharField(max_length=300, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    card_number = models.CharField(max_length=50, blank=True, null=True)
    authorization_code = models.CharField(max_length=50, blank=True, null=True)
    clearing_institute_name = models.CharField(max_length=100, blank=True, null=True)
    ipCountry = models.CharField(max_length=50, blank=True, null=True)
    ipAddr = models.CharField(max_length=50, blank=True, null=True)
    payment_confirmer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.applicant_id.full_name
