from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save, post_migrate
from registration.models.univStructure import Faculty, FACULTY_CHOICES
from registration.apps import RegistrationConfig


class Signal:
    SIGNAL_FACULTY = False


# send signal when faculty has been changed or added

@receiver(post_save, sender=Faculty)
def faculty_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_FACULTY = True


# send signal when faculty has been deleted

@receiver(post_delete, sender=Faculty)
def faculty_delete(sender, instance, **kwargs):
    Signal.SIGNAL_FACULTY = True


# send signal when listen to migrate on database

@receiver(post_migrate, sender=RegistrationConfig)
def faculty_migrate(sender, **kwargs):
    if not Faculty.objects.all().exists():
        fac = dict(FACULTY_CHOICES)
        for fa in fac:
            Faculty(
                name=fa
            ).save()
