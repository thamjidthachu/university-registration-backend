from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from registration.models.chat import Message, Conversation


class Signal:
    SIGNAL_MESSAGE = False
    SIGNAL_CONVERSATION = False


# send signal when message has been changed or added
@receiver(post_save, sender=Message)
def message_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_MESSAGE = True


# send signal when applicant has been deleted

@receiver(post_delete, sender=Message)
def message_delete(sender, instance, **kwargs):
    Signal.SIGNAL_MESSAGE = True


# send signal when conversation has been changed or added

@receiver(post_save, sender=Conversation)
def conversation_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_CONVERSATION = True


# send signal when applicant has been deleted

@receiver(post_delete, sender=Conversation)
def conversation_delete(sender, instance, **kwargs):
    Signal.SIGNAL_CONVERSATION = True
