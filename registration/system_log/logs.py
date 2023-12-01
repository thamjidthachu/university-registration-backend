from registration.models.system_log import SystemLog
from registration.models.user_model import User


def Logs(user, modified_to, old, modified, date):
    # get roles choice for user
    role = dict(User.USER_ROLES)

    # get gender choices for user
    gender = dict(User.GENDER_CHOICES)

    # save logs
    SystemLog(
        full_name=user.full_name,
        email=user.email,
        date_modified=date,
        role=role[user.role].replace("_", " "),
        gender=gender[user.gender],
        modified_to=modified_to,
        before_modified=old,
        modified_in=modified
    ).save()
