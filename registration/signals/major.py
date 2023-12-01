from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save, post_migrate
from registration.models.univStructure import Major, MAJOR_CHOICES, Faculty
from registration.apps import RegistrationConfig


class Signal:
    SIGNAL_MAJOR = False


# send signal when major has been changed or added

@receiver(post_save, sender=Major)
def major_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_MAJOR = True


# send signal when major has been deleted

@receiver(post_delete, sender=Major)
def major_delete(sender, instance, **kwargs):
    Signal.SIGNAL_MAJOR = True


# send signal when listen to migrate on database

@receiver(post_migrate, sender=RegistrationConfig)
def major_migrate(sender, **kwargs):
    if not Major.objects.all().exists():
        maj = dict(MAJOR_CHOICES)
        fac = Faculty.objects.all()
        keys = list(maj.keys())

        Major(
            faculty_id=fac[0],
            name=keys[0]
        ).save()
        maj.pop('MS')

        Major(
            faculty_id=fac[1],
            name=keys[1]
        ).save()
        maj.pop('PHD')

        maj.pop('NM')
        for ma in maj:
            Major(
                faculty_id=fac[2],
                name=ma
            ).save()

        Major(
            faculty_id=fac[3],
            name='NM'
        ).save()
