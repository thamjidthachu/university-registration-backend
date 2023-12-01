from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from registration.models.applicant import Files


class Signal:
    SIGNAL_DOCUMENTS = False


# send signal when documents have been changed or added
@receiver(post_save, sender=Files)
def documents_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_DOCUMENTS = True


# send signal when documents have been deleted
@receiver(post_delete, sender=Files)
def documents_delete(sender, instance, **kwargs):
    Signal.SIGNAL_DOCUMENTS = True

