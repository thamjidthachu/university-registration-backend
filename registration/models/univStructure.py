from django.conf import settings
from django.db import models

FACULTY_CHOICES = (
    ("M", "Medicine"),
    ("PH", "Pharmacy"),
    ("AS", "Applied Science"),
    ("NF", "No Faculty")
)

MAJOR_CHOICES = (
    ("MS", "Medicine & Surgery"),
    ("PHD", "Pharm D"),
    ("NU", "Nursing"),
    ("RT", "Respiratory Therapy"),
    ("EMS", "Emergency Medical Services"),
    ("AT", "Anaesthesia Technology"),
    ("HIS", "Health Information Systems"),
    ("IS", "Information Systems"),
    ("CS", "Computer Science"),
    ("IE", "Industrial Engineering"),
    ("GSE", "General science & English"),
    ("MEDN", "Master of Emergency and Disaster Nursing"),
    ("MCP", "Master of Clinical Pharmacy"),
    ("MCS", "Master of Cyber Security"),
    ("NM", "No Major"),
)
MAJOR_CHOICES_ARABIC = {
    "MS": "الطب والجراحة",
    "PHD": "دكتور صيدلة",
    "NU": "التمريض",
    "RT": "الرعاية التنفسية",
    "EMS": "الخدمات الطبية الطارئة",
    "AT": "تقنية التخدير",
    "HIS": "نظم المعلومات الصحية",
    "IS": "نظم المعلومات",
    "CS": "علوم الحاسب",
    "IE": "الهندسة الصناعية",
    "GSE": "قسم العلوم العامة و اللغة الانجليزية",
    "MEDN": "ماجستير تمريض الطوارئ والكوارث ",
    "MCP": "ماجستير الصيدلة الإكلينيكية",
    "MCS": "ماجستير  الأمن السيبراني",
}


class Faculty(models.Model):
    name = models.CharField(choices=FACULTY_CHOICES, max_length=10, unique=True)

    def __str__(self):
        return dict(FACULTY_CHOICES)[self.name]


class Major(models.Model):
    faculty_id = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="faculties")
    name = models.CharField(max_length=10, choices=MAJOR_CHOICES, unique=True)
    status = models.BooleanField(default=True)
    status_m = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    action_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return dict(MAJOR_CHOICES)[self.name]
