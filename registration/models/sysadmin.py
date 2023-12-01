from django.db import models
from .user_model import User

ROLES = (
    (1, "Applicant"),
    (2, "Admission Department"),
    (3, "English Department"),
    (4, "Scholarships Department"),
    (5, "Supervisor Department"),
    (6, "Admission Manager"),
    (7, "Pharmacy Dean"),
    (8, "Communication Department"),
    (9, "Medicine Dean"),
    (10, "Science Dean"),
    (11, "Register Review"),
    (12, "English Conformer"),
    (13, "Interview Test"),
    (14, "Equation Supervisor"),
    (15, "Head Of Department"),
    (16, "Registration"),
    (90, "Super Admin"),

)


class Permission(models.Model):
    group = models.IntegerField()
    descripton = models.CharField(max_length=100)


class UnivPayments(models.Model):
    PAY_TYPE = (
        ("ERET", "english_retest"),
        ("REG", "registration_fees"),
        ("EQU", "Equation Fees")
    )
    payment_title = models.CharField(max_length=10, choices=PAY_TYPE, unique=True)
    cost = models.FloatField()
    code = models.IntegerField()
    Trans_code = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_modified = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return dict(self.PAY_TYPE)[self.payment_title]


class Role(models.Model):
    role = models.PositiveIntegerField(choices=ROLES, unique=True)

    def __str__(self):
        return dict(ROLES)[self.role]
