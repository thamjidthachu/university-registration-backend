from django.core.management.base import BaseCommand

from registration.models.applicant import Applicant, Files


class Command(BaseCommand):
    help = 'Change the status of the files of the applicants'

    def handle(self, *args, **options):
        try:
            applicants = Applicant.objects.filter(registration_date__date='2023-08-06', init_state='UR')
            print(applicants.count())
            for i in applicants:
                print(i.full_name, "---", i.national_id)
                Files.objects.filter(applicant_id=i.id).update(status=None)
        except Exception as e:
            print(e)

        self.stdout.write(f'Successfully Completed.......')
