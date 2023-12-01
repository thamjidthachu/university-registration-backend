from django.db import models
from django.utils.translation import gettext_lazy as _


# Text Choices
class QualificationChoices(models.TextChoices):
    UE = 'UE', _('Uneducated')
    EL = 'EL', _('Elementary')
    INT = 'INT', _('Intermediate')
    HS = 'HS', _('High school')
    DP = 'DP', _('Diploma')
    UG = 'UG', _('Bachelors')
    PG = 'PG', _('Masters')
    DR = 'DR', _('Doctors')


class ContactResults(models.TextChoices):
    WA = 'WA', _('Will Attend')
    NR = 'NR', _('No Reply')
    WR = 'WR', _('Withdrew Registration')
    MM = 'MM', _('Major Medicine')
    NT = 'NT', _('Need Time')
    UP = 'UP', _('Uploading Process')


class DegreeChoices(models.TextChoices):
    UG = 'UG', _('Bachelors')
    PG = 'PG', _('Masters')


class InitStatChoices(models.TextChoices):
    UR = 'UR', _('Under Review')
    IA = 'IA', _('Initial Acceptance')
    CA = 'CA', _('Conditional Acceptance')
    RJ = 'RJ', _('Rejected')
    WR = 'WR', _('Withdrew Registration')


class FinalStatChoices(models.TextChoices):
    A = 'A', _('Accepted')
    RJ = 'RJ', _('Rejected')
    RJM = 'RJM', _('Rejected In Major')
    W = 'W', _('Put On waiting')


class GenderChoices(models.TextChoices):
    F = 'F', _('Female')
    M = 'M', _('Male')


class EvalChoices(models.TextChoices):
    S = 'S', _('Succeeded')
    F = 'F', _('Failed')
    L = 'L', _('Low Score')
    U = 'U', _('Unknown Certificate')


class ApplyChoices(models.TextChoices):
    FS = 'FS', _('Fresh Student')
    TS = 'TS', _('Transferred Student')
    HD = 'HD', _('Health Diploma Student')


class OfferChoices(models.TextChoices):
    AC = 'AC', _('Accepted')
    RJ = 'RJ', _('Rejected')


class FileStatChoices(models.TextChoices):
    A = 'A', _('Accepted')
    RJ = 'RJ', _('Rejected')


class StateUniversityChoices(models.TextChoices):
    RE = 'RE', _('Regular')
    OU = 'OU', _('Outgoing')
    AP = 'AP', _('Apologize')
    PP = 'PP', _('Postponed')
    AS = 'AS', _('Academically_separated')
    DD = 'DD', _('Disciplinary_disconnected')
    FR = 'FR', _('Folded_registration')
    GR = 'GR', _('Graduated')


# Integer Choices
class MaritalStatusChoices(models.IntegerChoices):
    SINGLE = 1, _('Single')
    MARRIED = 2, _('Married')
    DIVORCED = 3, _('Divorced')
    WIDOWED = 4, _('Widowed')


class EmployerChoices(models.IntegerChoices):
    GOVERNMENT = 1, _('Government')
    PRIVATE = 2, _('Private')
