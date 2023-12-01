from django.utils.deprecation import MiddlewareMixin
from tokens.views.tokenGenerator import token_generator
from django.http import HttpResponse


class authenticateMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # if request.path.split("/")[-1] not in ['register', 'login', 'forget', 'run', 'group', 'mail', 'verify',
        # 'export', 'report', 'phone', "reset","getcourses"] \ and 'media' not in request.path.split("/") \ and
        # 'admin' not in request.path.split("/"): if request.headers.get('auth-session') is None: return
        # HttpResponse("Unauthorized to access this link", status=403)

        user = token_generator.get_user_from_hash(request.headers.get('auth-session'))
        if user is not None:
            # return HttpResponse("Unauthorized to access this link", status=403)
            request.session['user'] = user
