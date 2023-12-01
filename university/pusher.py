import pusher
from django.conf import settings


class Pusher:

    def __init__(self, app_id, key, secret, cluster):

        self._pusher = pusher.Pusher(app_id=app_id, key=key, secret=secret, cluster=cluster)

    def get_pusher(self):
        return self._pusher


pusher_client = Pusher(app_id=settings.PUSHER_ID,
                       key=settings.PUSHER_KEY,
                       secret=settings.PUSHER_SECRET,
                       cluster=settings.PUSHER_CLUSTER
                       ).get_pusher()
