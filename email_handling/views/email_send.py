from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from smtplib import SMTPException
from rest_framework.exceptions import APIException
from attach_email.attach_email import get_attach_file
from django.conf import settings


class Mail:

    def __init__(self, domain, name, email, arabic_name=None, gender=None, link=None):
        
        if domain == "my.um.edu.sa":
            self._origin = f"https://{domain}"
        else:
            self._origin = f"http://{domain}"

        self._name = name
        self._arabic_name = arabic_name
        self._gender = gender
        self._to = email
        self._template_name = "body_mail_english.html"
        self._errors = APIException
        if link is None:
            self._link = f"{settings.DOMAIN_URL}/applicant/login"
        else:
            self._link = link

    def _get_body_string(self, subject, *args, **kwargs):
        return render_to_string(self._template_name, {
            "name": self._name,
            "arabic_name": self._arabic_name,
            "gender": self._gender,
            "kwargs": kwargs,
            "arabic": kwargs.pop("arabic"),
            "english": kwargs.pop('english'),
            "subject": subject,
            "domain": self._origin,
            "link": self._link,
        })

    def send(self, *args, **kwargs):
        subject = None
        from_email = None
        if 'subject' in kwargs:
            subject = kwargs.pop("subject")
        if 'from_email' in kwargs:
            from_email = kwargs.pop("from_email")

        if 'file' in kwargs:

            files = get_attach_file(kwargs.pop('file'))
        else:
            files = []

        mail = EmailMessage(
            subject=subject,
            body=self._get_body_string(subject, *args, **kwargs),
            from_email=from_email,
            to=[self._to],
            )
        mail.content_subtype = 'html'
        mail.mixed_subtype = 'related'
        for file in files:
            mail.attach(file['name'], file['file'], "text/html")

        try:
            mail.send()
            return True
        except SMTPException as e:
            raise self._errors(e)

    def get_errors(self):
        return self._errors.get_codes()
