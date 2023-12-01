from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from registration.models.evaluation import EnglishTest


class Signal:
    SIGNAL_ENGLISH = True


# send signal when english has been changed or added

@receiver(post_save, sender=EnglishTest)
def english_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_ENGLISH = True


# send signal when english has been deleted

@receiver(post_delete, sender=EnglishTest)
def english_delete(sender, instance, **kwargs):
    Signal.SIGNAL_ENGLISH = True
