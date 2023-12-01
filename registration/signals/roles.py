from django.dispatch import receiver
from django.db.models.signals import post_migrate
from registration.models.sysadmin import Role, ROLES
from registration.apps import RegistrationConfig


class Signal:
    SIGNAL_ROLE = False


# send signal on listening database migrations

@receiver(post_migrate, sender=RegistrationConfig)
def role_migrate(sender, **kwargs):
    all_roles = Role.objects.values_list('role', flat=True)
    roles = dict(ROLES)
    for role in roles:
        if role not in all_roles:
            Role(
                role=role
            ).save()
