from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save, post_migrate
from registration.apps import RegistrationConfig
from registration.models.user_model import User


class Signal:
    SIGNAL_USER = False


# send signal when user has been changed or added

@receiver(post_save, sender=User)
def user_create_update(sender, instance, **kwargs):
    Signal.SIGNAL_USER = True


# send signal when user has been deleted

@receiver(post_delete, sender=User)
def user_delete(sender, instance, **kwargs):
    Signal.SIGNAL_USER = True


# send signal when listen to migrate on database

@receiver(post_migrate, sender=RegistrationConfig)
def user_migrate(sender, **kwargs):
    if not User.objects.all().exists():
        #####
        # add admin account
        #####
        u = User.objects.create_superuser(
            email="admin@admin.com",
            userName="root",
            Phone="123",
            full_name="admin ",
            gender="M",
            password="django123"
        )
        u.save()
        default_user_test = {
            "admissionMale": {
                "email": "admission@male.com",
                "userName": "admission male",
                "Phone": "123",
                "role": 2,
                "gender": "M",
                "full_name": "admission male",
            },
            "admissionFemale": {
                "email": "admission@female.com",
                "userName": "admission female",
                "Phone": "123",
                "role": 2,
                "gender": "F",
                "full_name": "admission female",
            },
            "adminView": {
                "email": "admin@view.com",
                "userName": "admin view",
                "Phone": "123",
                "role": 11,
                "gender": "M",
                "full_name": "admin view",
            },
            "englishMale": {
                "email": "english@male.com",
                "userName": "english male",
                "Phone": "123",
                "role": 3,
                "gender": "M",
                "full_name": "english male",
            },
            "englishFemale": {
                "email": "english@female.com",
                "userName": "english female",
                "Phone": "123",
                "role": 3,
                "gender": "F",
                "full_name": "english female",
            },
            "englishConfirmer": {
                "email": "english@confirmer.com",
                "userName": "english confirmer",
                "Phone": "123",
                "role": 12,
                "gender": "M",
                "full_name": "english confirmer",
            },
            "interviewTestMale": {
                "email": "interviewtest@male.com",
                "userName": "interview test male",
                "Phone": "123",
                "role": 13,
                "gender": "M",
                "full_name": "interview test male",
            },
            "interviewTestFemale": {
                "email": "interviewtest@female.com",
                "userName": "interview test female",
                "Phone": "123",
                "role": 13,
                "gender": "F",
                "full_name": "interview test female",
            },
            "scholar": {
                "email": "scholar@male.com",
                "userName": "scholar male",
                "Phone": "123",
                "role": 4,
                "gender": "M",
                "full_name": "scholar male",
            },
            "deaanPharm": {
                "email": "dean@pharmacy.com",
                "userName": "pharmacy male",
                "Phone": "123",
                "role": 7,
                "gender": "M",
                "full_name": "pharmacy male",
            },
            "deaanMed": {
                "email": "dean@medicine.com",
                "userName": "medicine male",
                "Phone": "123",
                "role": 9,
                "gender": "M",
                "full_name": "medicine male",
            },
            "deaanApp": {
                "email": "dean@applied.com",
                "userName": "applied male",
                "Phone": "123",
                "role": 10,
                "gender": "M",
                "full_name": "applied male",
            },
            "admissionManager": {
                "email": "admission@manager.com",
                "userName": "admission manager",
                "Phone": "123",
                "role": 6,
                "gender": "M",
                "full_name": "admission manager",
            },
            "medSUPM": {
                "email": "supmale@medicine.com",
                "userName": "medicine & surgery Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "MS",
                "gender": "M",
                "full_name": "medicine & surgery male",
            },
            "medSUPF": {
                "email": "supfemale@medicine.com",
                "userName": "medicine & surgery Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "MS",
                "gender": "F",
                "full_name": "medicine & surgery female",
            },
            "phdSUPM": {
                "email": "supmale@pharmacy.com",
                "userName": "pharmacy Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "PHD",
                "gender": "M",
                "full_name": "pharmacy male",
            },
            "phdSUPF": {
                "email": "supfemale@pharmacy.com",
                "userName": "pharmacy Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "PHD",
                "gender": "F",
                "full_name": "pharmacy Female",
            },
            "nuSUPM": {
                "email": "supmale@nursing.com",
                "userName": "nursing Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "NU",
                "gender": "M",
                "full_name": "nursing male",
            },
            "nuSUPF": {
                "email": "supfemale@nursing.com",
                "userName": "nursing Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "NU",
                "gender": "F",
                "full_name": "nursing Female",
            },
            "rtSUPM": {
                "email": "supmale@respiratory.com",
                "userName": "respiratory therapy Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "RT",
                "gender": "M",
                "full_name": "respiratory therapy male",
            },
            "rtSUPF": {
                "email": "supfemale@respiratory.com",
                "userName": "respiratory therapy Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "RT",
                "gender": "F",
                "full_name": "respiratory therapy Female",
            },
            "emsSUPM": {
                "email": "supmale@emergency.com",
                "userName": "emergency medical services Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "EMS",
                "gender": "M",
                "full_name": "emergency medical services male",
            },
            "emsSUPF": {
                "email": "supfemale@emergency.com",
                "userName": "emergency medical services Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "EMS",
                "gender": "F",
                "full_name": "emergency medical services Female",
            },
            "atSUPM": {
                "email": "supmale@anaesthesia.com",
                "userName": "anaesthesia technology Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "AT",
                "gender": "M",
                "full_name": "anaesthesia technology male",
            },
            "atSUPF": {
                "email": "supfemale@anaesthesia.com",
                "userName": "anaesthesia technology Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "AT",
                "gender": "F",
                "full_name": "anaesthesia technology Female",
            },
            "hisSUPM": {
                "email": "supmale@health.com",
                "userName": "health information system Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "HIS",
                "gender": "M",
                "full_name": "health information system male",
            },
            "hisSUPF": {
                "email": "supfemale@health.com",
                "userName": "health information system Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "HIS",
                "gender": "F",
                "full_name": "health information system Female",
            },
            "isSUPM": {
                "email": "supmale@information.com",
                "userName": "information system Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "IS",
                "gender": "M",
                "full_name": "information system male",
            },
            "isSUPF": {
                "email": "supfemale@information.com",
                "userName": "information system Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "IS",
                "gender": "F",
                "full_name": "information system Female",
            },
            "csSUPM": {
                "email": "supmale@computer.com",
                "userName": "computer science Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "CS",
                "gender": "M",
                "full_name": "computer science male",
            },
            "csSUPF": {
                "email": "supfemale@computer.com",
                "userName": "computer science Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "CS",
                "gender": "F",
                "full_name": "computer science Female",
            },
            "ieSUPM": {
                "email": "supmale@engineering.com",
                "userName": "industrial engineering Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "IE",
                "gender": "M",
                "full_name": "industrial engineering male",
            },
            "ieSUPF": {
                "email": "supfemale@engineering.com",
                "userName": "industrial engineering Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "IE",
                "gender": "F",
                "full_name": "industrial engineering Female",
            },
            "gseSUPM": {
                "email": "supmale@science.com",
                "userName": "general science & english Supervisor male",
                "Phone": "123",
                "role": 14,
                "user_major": "GSE",
                "gender": "M",
                "full_name": "general science & english male",
            },
            "gseSUPF": {
                "email": "supfemale@science.com",
                "userName": "general science & english Supervisor female",
                "Phone": "123",
                "role": 14,
                "user_major": "GSE",
                "gender": "F",
                "full_name": "general science & english Female",
            },
            "interviewMaleM": {
                "email": "mmale@interview.com",
                "userName": "interview medicine male",
                "Phone": "123",
                "role": 5,
                "user_major": "M",
                "gender": "M",
                "full_name": "interview medicine male",
            },
            "interviewMalePH": {
                "email": "phmale@interview.com",
                "userName": "interview pharmacy male",
                "Phone": "123",
                "role": 5,
                "user_major": "PH",
                "gender": "M",
                "full_name": "interview pharmacy male",
            },
            "interviewMaleAS": {
                "email": "asmale@interview.com",
                "userName": "interview applied science male",
                "Phone": "123",
                "role": 5,
                "user_major": "AS",
                "gender": "M",
                "full_name": "interview applied science male",
            },
            "interviewFemaleM": {
                "email": "mfemale@interview.com",
                "userName": "interview medicine female",
                "Phone": "123",
                "role": 5,
                "user_major": "M",
                "gender": "F",
                "full_name": "interview medicine female",
            },
            "interviewFemalePH": {
                "email": "phfemale@interview.com",
                "userName": "interview pharmacy female",
                "Phone": "123",
                "role": 5,
                "user_major": "PH",
                "gender": "F",
                "full_name": "interview pharmacy female",
            },
            "interviewFemaleAS": {
                "email": "asfemale@interview.com",
                "userName": "interview applied science female",
                "Phone": "123",
                "role": 5,
                "user_major": "AS",
                "gender": "F",
                "full_name": "interview applied science female",
            },
        }
        for user in list(default_user_test.keys()):
            u = User(email=default_user_test[user]['email'],
                     role=default_user_test[user]['role'],
                     userName=default_user_test[user]['userName'],
                     Phone="123",
                     full_name=default_user_test[user]['full_name'],
                     gender=default_user_test[user]['gender'],
                     )
            u.set_password("django123")
            u.save()
