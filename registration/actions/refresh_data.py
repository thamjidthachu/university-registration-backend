from django.http import HttpResponseRedirect
from django.contrib import messages
# from registration.scripts.import_ereg_data import import_ereg_data
from django.conf import settings


class importEregData:

    def refresh_ereg_data(self, request):
        # import_ereg_data()
        self.message_user(
            request, "Succsessfully updated the data from ereg",
            messages.SUCCESS) if import_ereg_data() else self.message_user(
            request, "Can\'t update the data from ereg", messages.ERROR)
        return HttpResponseRedirect("../../")

    class Media:
        css = {
            'all': (f'{settings.STATIC_URL}user/css/user_model.css',)
        }
