from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from registration.models.evaluation import Interview


class Signal:
    SIGNAL_INTERVIEW = False


# send signal when interview has been changed or added

@receiver(post_save, sender=Interview)
def interview_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_INTERVIEW = True


# send signal when interview has been deleted

@receiver(post_delete, sender=Interview)
def interview_delete(sender, instance, **kwargs):
    Signal.SIGNAL_INTERVIEW = True
