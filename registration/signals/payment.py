from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from registration.models.applicant import Payment


class Signal:
    SIGNAL_PAYMENT = False


# send signal when payment has been changed or added

@receiver(post_save, sender=Payment)
def payment_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_PAYMENT = True


# send signal when payment has been deleted

@receiver(post_delete, sender=Payment)
def payment_delete(sender, instance, **kwargs):
    Signal.SIGNAL_PAYMENT = True
