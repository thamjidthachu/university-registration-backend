from django.db import models

SENDER_RECEIVER_CHOICES = (
    (2, 'Admin'),
    (1, 'Applicant'),
)

CONVERSATION_TYPE_CHOICES = (
    (1, 'Private'),
    (2, 'Group'),
)

MESSAGE_TYPE_CHOICES = (
    (1, 'Text'),
    (2, 'File'),
    (3, 'Emoji'),
    (4, 'Image'),
    (0, 'Other'),
)


# this class is used for save any message from conversation
class Message(models.Model):
    message = models.TextField()
    message_type = models.PositiveSmallIntegerField(choices=MESSAGE_TYPE_CHOICES)
    conversation = models.ForeignKey('Conversation', related_name='message_conversation', on_delete=models.CASCADE)
    participants = models.ManyToManyField('Participants', related_name='participants_message',
                                          through='MessageParticipants')
    delivered = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


# this class is make a conversation between User and applicant
class Conversation(models.Model):
    channel_name = models.SlugField(unique=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    conversation_type = models.PositiveSmallIntegerField(choices=CONVERSATION_TYPE_CHOICES)
    user_type_creator = models.PositiveSmallIntegerField(choices=SENDER_RECEIVER_CHOICES)
    user_creator = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    deleted = models.DateTimeField(blank=True, null=True)


class Participants(models.Model):
    user_type = models.PositiveSmallIntegerField(choices=SENDER_RECEIVER_CHOICES)
    user = models.PositiveIntegerField()
    last_online = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    conversation = models.ManyToManyField(Conversation, through='ConversationParticipants',
                                          related_name='conversation_participants')

    class Meta:
        unique_together = ('user_type', 'user',)
        verbose_name = "Participant"
        verbose_name_plural = "Participants"


class ConversationParticipants(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participants, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Conversation Participant"
        verbose_name_plural = "Conversation Participants"


class MessageParticipants(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participants, on_delete=models.CASCADE)
    receiver = models.BooleanField(default=True)
    seen = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Message Participant"
        verbose_name_plural = "Message Participants"
