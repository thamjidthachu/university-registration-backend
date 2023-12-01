from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from registration.models.applicant import Reservation


class Signal:
    SIGNAL_RESERVATION = True


# send signal when reservation has been changed or added

@receiver(post_save, sender=Reservation)
def reservation_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_RESERVATION = True


# send signal when reservation has been deleted

@receiver(post_delete, sender=Reservation)
def reservation_delete(sender, instance, **kwargs):
    Signal.SIGNAL_RESERVATION = True
