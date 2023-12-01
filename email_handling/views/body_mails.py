from registration.models.univStructure import Major

ARABIC_MAJORS_MAPPER = {
    "MS": "الطب والجراحة",
    "PHD": "دكتور صيدلة",
    "NU": "التمريض",
    "RT": "الرعاية التنفسية",
    "EMS": "الخدمات الطبية الطارئة",
    "AT": "تقنية التخدير",
    "HIS": "نظم المعلومات الصحية",
    "IS": "نظم المعلومات",
    "CS": "علوم الحاسب",
    "IE": "الهندسة الصناعية",
    "GSE": "قسم العلوم العامة و اللغة الانجليزية"
}

ENGLISH_MAJORS_MAPPER = {
    "MS": "Medicine & Surgery",
    "PHD": "Pharm D",
    "NU": "Nursing",
    "RT": "Respiratory Therapy",
    "EMS": "Emergency Medical Services",
    "AT": "Anaesthesia Technology",
    "HIS": "Health Information Systems",
    "IS": "Information Systems",
    "CS": "Computer Science",
    "IE": "Industrial Engineering",
    "GSE": "General science & English"
}

ENGLISH_CERTIFICATE_MAPPER = {
    'HS': 'High School Certificate',
    'AC': 'Certified Academic Record',
    'BDC': 'Bachelor Degree Certificate',
    'DC': 'Diploma Certificate',
    'IC': 'Certificate of Completion Internship'
}

ARABIC_CERTIFICATE_MAPPER = {
    'HS': 'أصل الشهادة الثانوية العامة',
    'AC': 'أصل السجل الأكاديمي',
    'BDC': 'أصل شهادة البكالوريوس',
    'DC': 'أصل شهادة الدبلوم',
    'IC': 'أصل شهادة الإمتياز'
}
# dean mail


def deanMail(object, major, majorArab):
    return {
        "english": (
            "The college has Reviewed your application.",
            ("Congratulations Your Application has been Accepted in Major " + major + \
             " with ALMaarefa University." if "A" == object.final_state else \
                 "Your application is on the waiting list" \
                     if "W" == object.final_state else \
                     "Unfortunately, Your application has been rejected" \
                         if "RJ" == object.final_state else \
                         "Unfortunately, Your application has not been selected for Major " + major + "\
                             in ALMaarefa University ,However you have another chance to be accepted into another major."
             ),
            (
                "To complete the procedures, please  visit your Dashboard and pay the fees." if "A" == object.final_state else ""),
            ("Note: the priority of seats is for those who complete the final admission procedures and pay the fees." \
                 if "A" == object.final_state else ""),
        ),
        "arabic": (
            "تم مراجعة طلبك من قبل الكلية",
            (
                "نهنئك بقبولك في تخصص  " + majorArab + \
                " في جامعة المعرفة" if "A" == object.final_state else \
                    "طلبك في قائمة الانتظار" \
                        if "W" == object.final_state else \
                        "تم رفض طلبك نهائياً." \
                            if "RJ" == object.final_state else \
                            "تم رفض طلبك في تخصص  " + majorArab + \
                            "في جامعة المعرفة ولديك فرصة اخرى للقبول في الرغبات الاخرى"
            ),
            ("لإكمال الإجراءات النهائية ، يرجى زيارة الرابط التالي و دفع الرسوم" if "A" == object.final_state else ""),
            (
                "ملاحظة: المقاعد محدودة  وأولوية القبول لمن ينهي إجراءات القبول و السداد أولا" if "A" == object.final_state else ""),
            ("يرجى زيارة الرابط التالي لاكمال الاجراءات النهائية" \
                 if "A" == object.final_state else ""),
        ),
    }


# admission mail

def admissionMail(obj, files=tuple()):
    init_state = obj.init_state
    has_english_cert = obj.applicants.filter(file_name='english_certf').exists()
    english_cert_null = obj.applicants.filter(file_name='english_certf', status__isnull=True).exists()
    ia_or_ca = init_state in ["IA", "CA"]

    def english_part():
        if ia_or_ca:
            return (
                "Verifying your English certificate." if english_cert_null else
                "Schedule your English language test by logging into your account." if (
                        obj.applicants.filter(file_name='english_certf', status='RJ').exists() or not has_english_cert
                ) else ""
            )
        return ""

    def arabic_part():
        if ia_or_ca:
            return (
                "جاري التحقق من شهادة اللغة الانجليزية." if english_cert_null else
                "نأمل الدخول على حسابك لحجز موعد لاختبار اللغة الانجليزية." if (
                        obj.applicants.filter(file_name='english_certf', status='RJ').exists() or not has_english_cert
                ) else ""
            )
        return ""

    return {
        "english": (
            "Your Application has been reviewed",
            "Your Application is Initially Accepted." if init_state == "IA" else
            "Sorry, Your application is Rejected." if init_state == "RJ" else
            "Your Application is Initially Accepted." if init_state == "CA" else "",
            english_part(),
            "We wish you the best of luck," if init_state == "IA" else "",
            "To complete the procedures, please visit your Dashboard and upload the updated documents." if files else "",
            "Rejected Files and Details Below: " if files else "",
            *files
        ),
        "arabic": (
            "تمت مراجعة طلبك",
            "و حالة الطلب قبول مبدئي" if init_state == "IA" else
            "تم رفض طلبك نهائيا" if init_state == "RJ" else
            "تم قبول طلبك " if init_state == "CA" else "",
            arabic_part(),
            "نتمنى لك التوفيق" if init_state == "IA" else "",
            "لإكمال إجراءات التقديم ، يرجى الدخول على الرابط  التالي و إعادة رفع الملف بعد التعديل" if files else "",
            "الملفات المرفوضة والتفاصيل أدناه: " if files else "",
            *files
        ),
    }


# admission re-upload mail

def admissionReuploadMail(object):
    return {
        "english": (
            "Files reuploaded successfully",
            (" Kindly be informed that the applicant " + str(object.full_name) + \
             " with National Id " + str(object.national_id) + \
             " has been re-uploaded the rejected files " \
             "Please check the files and change the initial state"),

        ),
        "arabic": (
            "تم اعادة رفع الملفات بنجاح",
            (
                    "الرجاء العلم ان الطالب" + str(object.arabic_full_name) + \
                    " برقم هوية " + str(object.national_id) + \
                    " اعاد رفع ملفاته المرفوضة " \
                    "الرجاء مراجعة الملفات وتغيير حالة الطالب المبدئية"
            ),

        ),
    }


# admission periority mail

def admissionPriorityMail(reason):
    return {
        "english": (
            "priorities have been updated",
            (" Kindly be informed that your priorites have been updated from the admission department "),
            ("due to"),
            (str(reason)),
            ("We wish you the best of luck"),

        ),
        "arabic": (
            "عزيزي / عزيزتي المتقدم/ ـة ",
            "تم تعديل الرغبات الخاصة بك",
            ("الرجاء العلم انه تم تعديل الرغبات الخاصة بك من قبل ادارة القبول والتسجيل "),
            (" سبب التعديل:"),
            (str(reason)),
            (" نتمني لك التوفيق ")

        )
    }


# english test mail

def englishTestMail(object):
    return {
        "english": (
            "Thank you for attending your English test.",
            "Your English Test Score is " + str(object.score),
            "Your English Test Result is " + "Passed" if True == object.confirmed else "We regret to tell you that you did not pass the English test. If you want to retake the test, you can log in to your account and follow the procedures.",
            "Log in to your account to schedule an admission interview." if True == object.confirmed else "",
            'We wish you the best of luck!',
        ),
        "arabic": (
            "نشكرك على حضور اختبار اللغة الانجليزية",
            "لقد نجحت في اختبار اللغة الانجليزية" if True == object.confirmed else \
                " لم تحصل على الدرجة المطلوبة في اختبار اللغة الانجليزية  إذا رغبت في إعادة الاختبار  يمكنك الدخول إلى حسابك وإكمال الاجراءات",
            "درجة الاختبار الخاصة بك هي " + str(object.score),
            "برجاء الدخول لحسابك وحجز موعد للمقابلة الشخصية" if True == object.confirmed else "",
            "نتمنى لك التوفيق",
        ),
    }


# english failed mail

def englishFailedMail():
    return {
        "english": (
            "Thank you for taking the English  test",
            "We regret to tell you that you did not pass the English test. If you want to retake the test, you can log in to your account and follow the procedures.",
            "We wish you the best of luck!",
        ),
        "arabic": (
            "نشكرك على حضور اختبار اللغة الانجليزية",
            " لم تحصل على الدرجة المطلوبة في اختبار اللغة الانجليزية  إذا رغبت في إعادة الاختبار  يمكنك الدخول إلى حسابك وإكمال الاجراءات",
            "نتمنى لك التوفيق",
        ),
    }


# english certified failed mail

def englishCertifiedFailedMail():
    return {
        "english": (
            "Thank you for uploading your English certificate",
            "We regret to tell you that your certificate has not been confirmed from the university so you can reserve an appointment to rake the English test by log in to your account and follow the procedures." \
            "We wish you the best of luck!",
        ),
        "arabic": (
            "نشكرك على رفع شهادة اللغة",
            " لم يتم اعتماد شهادة اللغة الخاصة بك من الجامعة يمكنك حجز موعد لاختبار اللغة من خلال الدخول إلى حسابك وإكمال الاجراءات" \
            "نتمنى لك التوفيق",
        ),
    }


# english certified Could Not Verify mail
def englishCertifiedNotVerifiedMail():
    return {
        "english": (
            "Thank you for uploading your English certificate",
            "Your certificate is unable to be verified. Please upload the English certificate again",
            "We wish you the best of luck!",
        ),
        "arabic": (
            "نشكرك على رفع شهادة اللغة",
            "لا يمكن التحقق من شهادتك. يرجى تحميل شهادة اللغة الإنجليزية مرة أخرى",
            "نتمنى لك التوفيق",
        ),
    }


# english postponed mail

def englishPostponedMail():
    return {
        "english": (
            "Thank you for choosing AlMaarefa University",
            "Kindly be informed that your English test has been postponed",
            "and we will reschedule the test appointment at the beginning of the semester ",
            'Meanwhile you can move to the next phase by reserving the Interview appointment from your Dashboard',
            "We wish you the best of luck",
        ),
        "arabic": (
            "نشكرك لاختيارك جامعة المعرفة",
            "سيتم جدولة اختبار تحديد مستوى اللغة الانجليزية فى بداية الفصل",
            "ويمكنك الآن اختيار موعد المقابلة الشخصية بالضغط على الرابط التالي",
            "نتمنى لك التوفيق",
        ),
    }


# english Absent mail

def englishAbsentMail():
    return {
        "english": (
            "Thank you for choosing AlMaarefa University",
            "Kindly be informed that you can reserve another English test appointment",
            'Please visit your dashboard and book your English test appointment',
            'We wish you the best of luck',
        ),
        "arabic": (
            "نشكرك لاختيارك جامعة المعرفة",
            "الرجاء العلم  أنه بإمكانك اختيار موعد اخر لحضور اختبار اللغة",
            "ويمكنك الآن زيارة صفحتك الشخصية وحجز الموعد من خلالها",
            "نتمنى لك التوفيق",
        ),
    }


# english send invitation mail

def englishSendInvitationMail():
    return {
        "english": (
            "Thank you for choosing AlMaarefa University",
            "Kindly be informed that you can start your English Test using this link",
            'We wish you the best of luck',
        ),
        "arabic": (
            "نشكرك لاختيارك جامعة المعرفة",
            "الرجاء العلم انه بإمكانك بدء اختبار اللغه من خلال زياره الرابط التالي",
            "نتمنى لك التوفيق",
        ),
    }


# interview send invitation mail

def interviewSendInvitationMail():
    return {
        "english": (
            "Thank you for choosing AlMaarefa University",
            "Kindly be informed that you can start your Interview Test using this link",
            'We wish you the best of luck',
        ),
        "arabic": (
            "نشكرك لاختيارك جامعة المعرفة",
            "الرجاء العلم انه بإمكانك بدء اختبار المقابلة من خلال زياره الرابط التالي",
            "نتمنى لك التوفيق",
        ),
    }


# english certificate mail

def englishCertificateMail(object):
    return {
        "english": (
            "Thank you for waiting English approve.",
            "Your English Certificate result is " +
            "Approved" if object.validated_data['english_certf_confirmation'] is True else "Rejected",
            'We wish you the best of luck!',
        ),
        "arabic": (
            "نشكرك  على رفع شهادة اللغة  الانجليزية",
            "تم قبول شهادة اللغة الانجليزية" if object.validated_data['english_certf_confirmation'] is True
            else "تم رفض شهادة اللغة الانجليزية",
            "نتمنى لك التوفيق"
        ),
    }


# interview mail


def interviewMail(object):
    return {
        "english": (
            "Thank you for attending Interview Test",
            ("You successfully Passed the Interview ." \
                 if "S" == str(object.result) else "Unfortunately, You did not pass the Interview"),
        ),
        "arabic": (
            "نشكرك على حضور المقابلة",
            "لقد نجحت في المقابلة" if "S" == str(object.result) else \
                "لقد رسبت في المقابلة"
        ),
    }


# interview absent mail


def interviewAbsentMail():
    return {
        "english": (
            "Thank you for choosing AlMaarefa University",
            "Kindly be informed that you can reserve another interview appointment",
            'Please visit your dashboard and book your interview appointment',
            'We wish you the best of luck',
        ),
        "arabic": (
            "نشكرك لاختيارك جامعة المعرفة",
            "الرجاء العلم  أنه بإمكانك اختيار موعد اخر لحضور المقابلة الشخصية",
            "ويمكنك الآن زيارة صفحتك الشخصية وحجز الموعد من خلالها",
            "نتمنى لك التوفيق",
        ),
    }


# Applicant

# applicant register mail

def registerMail():
    return {
        "english": (
            "Your account has been successfully created.",
            "Please use your Email and national ID to complete your registration.",
            "We wish you the best of luck",
        ),
        "arabic": (
            "تم إنشاء حسابك في جامعة المعرفة بنجاح",
            "يرجى تسجيل الدخول باستخدام بريدك الإلكتروني ورقم الهوية لإكمال عملية التسجيل",
            "نتمنى لك التوفيق"
        ),
    }


# applicant forget application id mail

def forgetPasswordMail():
    return {
        "english": (
            "Click this link to reset your password",
            "This link will be expired after 10 minutes",
            "Thank you",
        ),
        "arabic": (
            "قم بزيارة الرابط التالي لاستعاده كلمة المرور الخاصة بك",
            "يرجى العلم ان هذا الرابط سينتهي بعد 10 دقائق",
            "شكرا لك"
        ),
    }


# applicant upload mail

def uploadMail():
    return {
        "english": (
            "Thank you for Uploading your Documents.",
            "Your application is being processed.",
            "By visiting your dashboard, you can see the status of your application"
        ),
        "arabic": (
            "نشكرك على تحميل المستندات الخاصة بك",
            "طلبك قيد المراجعة",
            "و يمكنكم متابعة حالة الطلب من خلال الرابط التالي",
            "نتمنى لك التوفيق"
        ),
    }


# applicant Offer mail

def offerMail(object):
    return {
        "english": (),
        "arabic": (),
    }


# applicant english book mail

def englishBookMail_online(object):
    return {
        "english": (
            'Thank you for booking an appointment for the English test.',
            "English test will be on  " \
            + str(object.reservation_date) + " at " \
            + str(object.start_time),
            "Note : The test will be through Zoom and the invitation link will be sent to your email. Please, read the attached file and do not miss this date.",
            "We wish you the best of luck",
        ),
        "arabic": (

            "نشكرك على حجز موعد لاختبار اللغة الإنجليزية",
            "وقت الاختبار يوم " + str(object.reservation_date) + "عند الساعة " \
            + str(object.start_time),
            "ملاحظة : الاختبار سيكون من خلال تطبيق زووم وسيتم ارسال رابط الجلسة في حينه على البريد الإلكتروني نرجو الالتزام بالموعد المحدد ، كما يرجى الاطلاع على الملف المرفق قبل موعد الاختبار",
            " نتمنى لك التوفيق",
        ),
    }


def englishBookMail_offline(object):
    return {
        "english": (
            'Thank you for booking an appointment for the English test.',
            "English test will be on  " \
            + str(object.reservation_date) + " at " \
            + str(object.start_time),
            "The test will take place on campus, make sure you arrive 15 minutes prior to the test.",
            "University location : ",
            "https://maps.app.goo.gl/L2nUSjffea63ZBnH6",
            "We wish you the best of luck",
        ),
        "arabic": (

            "نشكرك على حجز موعد لاختبار اللغة الإنجليزية",
            "وقت الاختبار يوم " + str(object.reservation_date) + "عند الساعة " \
            + str(object.start_time),
            "الاختبار سيكون داخل الحرم الجامعي، وعليك الحضور قبل الموعد ب(10) دقيقة استعداداً لأداء الاختبار.",
            " : موقع الجامعة على الخريطة ",
            "https://maps.app.goo.gl/L2nUSjffea63ZBnH6",
            " نتمنى لك التوفيق",
        ),
    }


# applicant interview Book mail

def interviewBookMail_online(object):
    return {
        "english": (
            "Thank you for booking your interview appointment",
            "Your Interview will be on " + str(object.reservation_date) + " at " + str(object.start_time),
            "Note : Interview will be through Zoom and the invitation link will be sent to your email. Please read the attached file and do not miss this date. ",
        ),
        "arabic": (
            "نشكرك على حجز موعد المقابلة",
            "موعد المقابلة يوم " + str(object.reservation_date) + "عند الساعة " \
            + str(object.start_time),
            "ملاحظة : المقابلة ستكون من خلال تطبيق زووم وسيتم ارسال رابط الجلسة في حينه على البريد الإلكتروني  نرجو الالتزام بالموعد المحدد ، كما يرجى الاطلاع على الملف المرفق"
        ),
    }


def interviewBookMail_offline(object):
    return {
        "english": (
            'Thank you for booking your interview appointment.',
            "Your Interview will be on  " \
            + str(object.reservation_date) + " at " \
            + str(object.start_time),
            "The interview will take place on campus, make sure you arrive 15 minutes prior to the test.",
            "University location : ",
            "https://maps.app.goo.gl/L2nUSjffea63ZBnH6",
            "We wish you the best of luck",
        ),
        "arabic": (

            "نشكرك على حجز موعد للمقابلة الشخصية",
            "وقت المقابلة يوم " + str(object.reservation_date) + "عند الساعة " \
            + str(object.start_time),
            "المقابلة ستكون داخل الحرم الجامعي، وعليك الحضور قبل الموعد ب(10) دقيقة استعداداً لأداء المقابلة.",
            " : موقع الجامعة على الخريطة ",
            "https://maps.app.goo.gl/L2nUSjffea63ZBnH6",
            " نتمنى لك التوفيق",
        ),
    }


# applicant payment mail

def paymentMail(object):
    return {
        "english": (
            "Your payment has been received successfully, Thank you",
            "Transaction amount " + str(object.payment_id.cost)
        ),
        "arabic": (
            "تم عملية دفع",
            "تم دفع مبلغ قدره " + str(object.payment_id.cost) + "رسوم إعادة الاختبار" \
                if object.payment_id.payment_title == "ERET" else 'رسوم طلب المعادلة' if object.payment_id.payment_title == "EQU" else "رسوم قبولك في الجامعة"
        ),
    }


# send mail after get student id


def StudentIDMail(applicant):
    if applicant.gender == "M":
        return {
            "english": (
                "Dear applicant,"
                "we congratulate you on your admission to Al-Maarefa University."
                "You can submit a request for course equivalency and pay equivalency fees through the application platform,"
                "with our best wishes for success.",
            ),
            "arabic": (
                "عزيزي المتقدم نبارك لك قبولك في جامعة المعرفة و يمكنك رفع طلب معادله المقررات الدراسية  وسداد رسوم المعادله من خلال منصه التقديم  مع تمنياتنا لكم بالتوفيق."
            ),
        }
    else:
        return {
            "english": (
                "Dear applicant,"
                "we congratulate you on your admission to Al-Maarefa University."
                "You can submit a request for course equivalency and pay equivalency fees through the application platform,"
                "with our best wishes for success.",
            ),
            "arabic": (
                "عزيزتي المتقدمـة نبارك لك قبولك في جامعة المعرفة ويمكنك رفع طلب معادله المقررات الدراسية  وسداد رسوم المعادله من خلال منصه التقديم  مع تمنياتنا لكم بالتوفيق  ."
            ),
        }


# send mail after get student id for tajseer or transferred
def StudentIDNotFreshMail(applicant):
    if applicant.gender == "M":
        return {
            "english": (
                "Dear applicant,"
                "we congratulate you on your admission to Al-Maarefa University."
                "You can submit a request for course equivalency and pay equivalency fees through the application platform,"
                "with our best wishes for success.",
            ),
            "arabic": (
                "عزيزي المتقدم نبارك لك قبولك في جامعة المعرفة و يمكنك رفع طلب معادله المقررات الدراسية  وسداد رسوم المعادله من خلال منصه التقديم  مع تمنياتنا لكم بالتوفيق  ."
            ),
        }
    else:
        return {
            "english": (
                "Dear applicant,"
                "we congratulate you on your admission to Al-Maarefa University."
                "You can submit a request for course equivalency and pay equivalency fees through the application platform,"
                "with our best wishes for success.",
            ),
            "arabic": (
                "عزيزتي المتقدمـة نبارك لك قبولك في جامعة المعرفة ويمكنك رفع طلب معادله المقررات الدراسية  وسداد رسوم المعادله من خلال منصه التقديم  مع تمنياتنا لكم بالتوفيق  ."
            ),
        }


# old system mail

def oldsystemMail(object):
    return {
        "english": (
            "Your account has been created into Al Maarefa university.",
            "Please login with your Email and National ID to complete your registration.",
        ),
        "arabic": (
            "تم إنشاء حسابك في جامعة المعرفة بنجاح",
            "يرجى تسجيل الدخول باستخدام بريدك الالكتروني ورقم الهوية لاكمال عملية التسجيل",
        ),
    }


# Student Equation Created Email

def studentEquationCreatedMail():
    return {
        "english": (
            "We have received your equation request.",
            "Your equation request is under review and you will be notified when it's updated.",
        ),
        "arabic": (
            "تم استلام طلب المعادلة الخاصة بك.",
            "طلب المعادلة قيد المراجعة وسيتم إشعارك فور تحديثها.",
        ),
    }


# Student Equation Confirmed Email

def studentEquationUpdateMail():
    return {
        "english": (
            "Your equation request has been updated.",
            "Please login with your Email and Password to view the update.",
        ),
        "arabic": (
            "لديك تحديث على طلب المعادلة الخاصة بك.",
            "يرجى تسجيل الدخول باستخدام بريدك الالكتروني ورقم الهوية للإطلاع على التحديث.",
        ),
    }


def CertificateSubmissionMail(files, to_submit):
    ar_files = ["- " + ARABIC_CERTIFICATE_MAPPER[file] for file in files]
    en_files = ["- " + ENGLISH_CERTIFICATE_MAPPER[file] for file in files]
    body = {
        "english": (
            "We congratulate you on your admission to Al-Maarefa University and inform you that the original "
            "documents have been received",
            *en_files,
            'which will be returned upon graduation or withdrawal from the university',
            'We wish you the best of luck',
        ),
        "arabic": (
            "نبارك لكم قبولكم في جامعة المعرفة ونفيدكم بأنه تم أستلام أصل الوثائق",
            *ar_files,
            "سيتم إعادته عند التخرج أو الانسحاب من الجامعة",
            "نتمنى لك التوفيق",
        ),
    }
    if bool(to_submit):
        en_to_submit = ["- " + ENGLISH_CERTIFICATE_MAPPER[file] for file in to_submit]
        ar_to_submit = ["- " + ARABIC_CERTIFICATE_MAPPER[file] for file in to_submit]
        body = {
            "english": (
                "We congratulate you on your admission to Al-Maarefa University and inform you that the original "
                "documents have been received",
                *en_files,
                'which will be returned upon graduation or withdrawal from the university',
                'Certificates to be submitted:',
                *en_to_submit,
                'We wish you the best of luck',
            ),
            "arabic": (
                "نبارك لكم قبولكم في جامعة المعرفة ونفيدكم بأنه تم أستلام أصل الوثائق",
                *ar_files,
                "سيتم إعادته عند التخرج أو الانسحاب من الجامعة",
                "الشهادات المطلوب تقديمها:",
                *ar_to_submit,
                "نتمنى لك التوفيق",
            ),
        }

    return body




