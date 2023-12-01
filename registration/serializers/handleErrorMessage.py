from django.utils.translation import gettext_lazy as _


def handle_error_msg(detail, params):
    if isinstance(detail, dict) and len(detail) == 1:
        return _(detail[list(detail.keys())[0]]) % params
    elif isinstance(detail, dict) and len(detail) > 1:
        return None
    if isinstance(detail, str):
        return _(detail) % params
