from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    class manager for providing a User(AbstractBaseUser) full control
    on these objects to create all types of User and these roles.
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        pass data  to '_create_user' for creating normal_user .
        """
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        pass data to '_create_user' for creating super_user .
        """
        if email is None:
            raise TypeError('Users must have an email address.')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 90)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    create class User from Abstraction and Permissions (from low_level) to give us
    full control to create user with role and other options not include in normal user
    """
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('A', 'All'),
    )
    USER_ROLES = (
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
        ("M", "Medicine"),
        ("PH", "Pharmacy"),
        ("AS", "Applied Science"),
        ("MEDN", "Master of Emergency and Disaster Nursing"),
        ("MCP", "Master of Clinical Pharmacy"),
        ("MCS", "Master of Cyber Security"),
        ("NM", "No Major"),
    )
    full_name = models.CharField(max_length=150)
    userName = models.CharField(max_length=50)
    email = models.EmailField(db_index=True, unique=True)
    Phone = models.CharField(max_length=50)
    role = models.PositiveIntegerField(choices=USER_ROLES)
    user_major = models.CharField(max_length=10, choices=MAJOR_CHOICES, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    signature = models.ImageField(blank=True, null=True)
    user_roles = models.ManyToManyField('registration.Role', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'gender']

    objects = UserManager()

    def __str__(self):
        return self.email
