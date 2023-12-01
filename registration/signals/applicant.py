from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from registration.models.applicant import Applicant


class Signal:
    SIGNAL_APPLICANT = False


# send signal when applicant has been changed or added
@receiver(post_save, sender=Applicant)
def applicant_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_APPLICANT = True


# send signal when applicant has been deleted
@receiver(post_delete, sender=Applicant)
def applicant_delete(sender, instance, **kwargs):
    Signal.SIGNAL_APPLICANT = True
