from django.apps import AppConfig


class RegistrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'registration'

    def ready(self):
        # add default data
        from django.db.models.signals import post_migrate
        from .signals.user import user_migrate
        from .signals.faculty import faculty_migrate
        from .signals.major import major_migrate
        # from .signals.lookup import lookup_migrate
        from .signals.roles import role_migrate

        # add school data
        # post_migrate.connect(lookup_migrate, sender=self)

        # add default users
        post_migrate.connect(user_migrate, sender=self)

        # add default faculty
        post_migrate.connect(faculty_migrate, sender=self)

        # add default majors
        post_migrate.connect(major_migrate, sender=self)

        # add default roles
        post_migrate.connect(role_migrate, sender=self)
