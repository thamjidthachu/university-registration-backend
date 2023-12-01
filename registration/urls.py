from django.urls import path

from registration.automatedScript import (
    OldSystemRun, AutomatedSendSmsUnregistered, AutomatedSendSmsWaitingPay
)
from registration.views.admin import (
    LoginAdmin, AdminProfile, statistics, UpdateRole
)
from registration.views.admin.admission import (
    absentApplicants, Admission, AddUser, AdmissionDate,
    AdmissionDisableMajor, AdmissionDisableApplicants, AdmissionEnglishGrade, AdmissionInterviewGrade, AdmissionAddNote,
    AdmissionUpdateMail, AdmissionUpdatePeriority, AdmissionUpdateScore, AdmissionUpload, SendCustomSms,
    UnregisteredApplicants, UpdateApplicant, AdmissionFileUpload, AdmissionApplicantOutSystem,
    EnglishCertificateRejected, EquationFeesExemptView, AdmissionOtherFileUpload, finalAcceptedApplicants,
    SendCustomEmail, PaymentByCash, CreateCertificateListView, SubmitCertificateListView
)
from registration.views.admin.admission.ExcelExportReports import (
    absentEnglishApplicantsExportXlsx, absentInterviewApplicantsExportXlsx, ApplicantExportXlsx,
    ApplicantFinalStateExportXlsx, applicantQuestionaireExportXlsx, applicantTrackExportXlsx, ContactCountsExportXlsx,
    nonPaidApplicantsExportXlsx, nonReservedEnglishApplicantsExportXlsx, nonReservedInterviewApplicantsExportXlsx,
    noResultEnglishApplicantsExportXlsx, noResultInterviewApplicantsExportXlsx, notFinalAcceptedApplicantsExport,
    PledgeFinalAccptedExportXlsx, registerationTimeAverageExportXlsx, ReportBuilder, unCompletedApplicantsExportXlsx,
    unRegisteredApplicantsExportXlsx, waitingApplicantsExportXlsx
)
from registration.views.admin.dean import (
    deanApplicantsExportXlsx, DeanEval, deanUpdateState
)
from registration.views.admin.englishTest import (
    CertifiedEnglishExportXlsx, EnglishCertificateConfirmGrade, EnglishCertificate, EnglishCertificateConfirm,
    EnglishCertificateGrade, EnglishConfirmData, EnglishConfirmGrade, EnglishExportXlsx, EnglishExportAllSemestersXlsx,
    EnglishGrade, EnglishReview, SendInvitation,
)
from registration.views.admin.scholarShip import (
    PaymentExportXlsx, PaymentReport, ScholarShipFees
)
from registration.views.admin.supervisor import (
    InterviewExportXlsx, InterviewGrade, InterviewSupervisor,
)
from registration.views.chat import (
    ConversationView, DeliveredView, MessageView, OnlineView, ParticipantView, SeenView, TypingView, UnreadMessages
)
from registration.views.user import (
    ApplicantPledge, ForgetPassword, InterviewBook, Login, ListLookupView, Register, UpdateMajor, UpdatePassword,
    Upload, VerifyEmail, VerifyNationalID, ApplicantOffer, ApplicantPay, BookDate, EnglishBook, Profile, SetPassword,
    Periority, VerifyPhone
)
from .views import (currentUserInfo, RegisterInfo, Logout, AllMajorsView)

app_name = 'registration'
urlpatterns = [

    # save data coming from old system
    path("old/system/run", OldSystemRun.as_view()),

    # send sms message to unregistered into the system
    path("sms/unregistered/run", AutomatedSendSmsUnregistered.as_view()),

    # send sms message to not pay the register fees into the system
    path("sms/waiting/pay/run", AutomatedSendSmsWaitingPay.as_view()),

    # check email
    path("auth/email/verify", VerifyEmail.as_view()),

    # Check national id
    path("auth/nationalid/verify", VerifyNationalID.as_view()),

    # Get lookup data
    path("applicant/lookup", ListLookupView.as_view()),

    # register new applicant
    path('auth/register', Register.as_view()),
    # login applicant only
    path('auth/applicant/login', Login.as_view()),
    # forget password
    path('auth/applicant/forget', ForgetPassword.as_view()),

    # update password
    path('auth/applicant/password/reset', UpdatePassword.as_view()),
    # profile applicant
    path('applicant/profile', Profile.as_view()),

    # set Password applicant
    path('applicant/password/set', SetPassword.as_view()),

    # login admin only
    path('auth/admin/login', LoginAdmin.as_view()),
    # get data from current user logged either user or applicant
    path('auth/current', currentUserInfo.as_view()),
    path('auth/info/register', RegisterInfo.as_view()),

    # logout url with destroy the session of user
    path('user/logout', Logout.as_view()),

    # add profile url for all admin
    path('role/profile', AdminProfile.as_view()),

    # update current role for all admins
    path('role/update', UpdateRole.as_view()),

    # process applicant
    path('applicant/upload', Upload.as_view()),
    path('applicant/book/interview', InterviewBook.as_view()),
    path("applicant/offer", ApplicantOffer.as_view()),
    path("applicant/periority/set", Periority.as_view()),
    path("applicant/verify/phone", VerifyPhone.as_view()),
    path("applicant/pledge", ApplicantPledge.as_view()),
    path("applicant/major/update", UpdateMajor.as_view()),
    # path("applicant/chat/rooms", applicant_rooms.as_view()),
    # path("applicant/chat", applicant_room.as_view()),

    # admin process
    # admission process

    # original certificate
    path('admission/certificate/add', CreateCertificateListView.as_view()),
    path('admission/certificate/submission', SubmitCertificateListView.as_view()),

    path('admission/applicant/update', UpdateApplicant.as_view()),
    path('admission/all/applicants', Admission.as_view()),
    path('admission/applicant', AdmissionUpload.as_view()),
    path('admission/applicant/email', SendCustomEmail.as_view()),
    path('admission/applicant/sms/message', SendCustomSms.as_view()),
    path("applicant/book/date/<type>", BookDate.as_view()),
    path("admission/dates/<type>", AdmissionDate.as_view()),
    path("admission/applicant/scores", AdmissionUpdateScore.as_view()),
    path('admission/all/unregistredapplicants', UnregisteredApplicants.as_view()),
    path("admission/applicant/mailupdate", AdmissionUpdateMail.as_view()),
    path("admission/applicant/periorityupdate", AdmissionUpdatePeriority.as_view()),
    path("admission/applicant/out/MajorUpdate", AdmissionApplicantOutSystem.as_view()),
    path("admission/applicant/finalAccept", finalAcceptedApplicants.as_view()),
    path("admission/applicant/notes", AdmissionAddNote.as_view()),
    path("admission/majors/disable", AdmissionDisableMajor.as_view()),
    path("admission/add/user", AddUser.as_view()),
    path("admission/grade/interview", AdmissionInterviewGrade.as_view()),
    path("admission/grade/english", AdmissionEnglishGrade.as_view()),
    path("admission/applicant/absent", absentApplicants.as_view()),
    path("admission/applicant/upload", AdmissionFileUpload.as_view()),
    path("admission/applicant/upload/other", AdmissionOtherFileUpload.as_view()),
    path("admission/applicant/equation/exempt/<int:pk>", EquationFeesExemptView.as_view()),
    path("admission/applicants/special-needs/", AdmissionDisableApplicants.as_view()),

    # admission reports exports
    path("admission/applicant/export", ApplicantExportXlsx.as_view()),
    path("admission/applicant/track/export", applicantTrackExportXlsx.as_view()),
    path("admission/applicant/final/export", ApplicantFinalStateExportXlsx.as_view()),
    path("admission/applicant/uncompleted/export", unCompletedApplicantsExportXlsx.as_view()),
    path("admission/applicant/unregistered/export", unRegisteredApplicantsExportXlsx.as_view()),
    path("admission/applicant/notEnglish/export", nonReservedEnglishApplicantsExportXlsx.as_view()),
    path("admission/applicant/notInterview/export", nonReservedInterviewApplicantsExportXlsx.as_view()),
    path("admission/applicant/nopaid/export", nonPaidApplicantsExportXlsx.as_view()),
    path("admission/applicant/absentEnglish/export", absentEnglishApplicantsExportXlsx.as_view()),
    path("admission/applicant/absentInterview/export", absentInterviewApplicantsExportXlsx.as_view()),
    path("admission/applicant/notResultEng/export", noResultEnglishApplicantsExportXlsx.as_view()),
    path("admission/applicant/notResultIn/export", noResultInterviewApplicantsExportXlsx.as_view()),
    path("admission/applicant/plegde/export", PledgeFinalAccptedExportXlsx.as_view()),
    path("admission/applicant/finalstate/none/export", notFinalAcceptedApplicantsExport.as_view()),
    path("admission/applicant/waiting/export", waitingApplicantsExportXlsx.as_view()),
    path("admission/applicant/counts/export", ContactCountsExportXlsx.as_view()),
    path("admission/applicant/questionaire/export", applicantQuestionaireExportXlsx.as_view()),
    path("admission/registeration/time/avg/export", registerationTimeAverageExportXlsx.as_view()),

    # payment by cash
    path("admission/applicant/cash/payment/<type>", PaymentByCash.as_view()),

    # dean process

    path('all/applicants', DeanEval.as_view()),
    path('applicant/final', deanUpdateState.as_view()),
    path('dean/applicant/export', deanApplicantsExportXlsx.as_view()),

    # supervisor process

    path('interview/applicants', InterviewGrade.as_view()),
    path('interview/applicant', InterviewSupervisor.as_view()),
    path('interview/applicants/export', InterviewExportXlsx.as_view()),

    # english Test process

    path("applicant/book/english", EnglishBook.as_view()),
    path("english/applicants", EnglishGrade.as_view()),
    path("english/applicant", EnglishReview.as_view()),
    path("english/certificate/applicants", EnglishCertificate.as_view()),
    path("english/certificate/applicant", EnglishCertificateGrade.as_view()),
    path("english/applicant/export", EnglishExportXlsx.as_view()),
    path("english/confirm/data", EnglishConfirmData.as_view()),
    path("english/confirm/grade", EnglishConfirmGrade.as_view()),
    path("english/certified/applicant/export", CertifiedEnglishExportXlsx.as_view()),
    path("english/certificate/confirm/data", EnglishCertificateConfirm.as_view()),
    path("english/certificate/rejected/data", EnglishCertificateRejected.as_view()),
    path("english/certificate/confirm/grade", EnglishCertificateConfirmGrade.as_view()),
    path("english/applicant/export/all", EnglishExportAllSemestersXlsx.as_view()),

    # send invitation url
    path("send/invitation", SendInvitation.as_view()),

    # scholar fees
    path("scholar/fees", ScholarShipFees.as_view()),

    # payment report
    path("scholar/payment", PaymentReport.as_view()),
    path("scholar/payment/export", PaymentExportXlsx.as_view()),

    # payment gateway
    path("applicant/pay/<type>", ApplicantPay.as_view()),

    # statistics
    path("system/report", statistics.as_view()),

    # get all majors
    path("major/all", AllMajorsView.as_view()),

    # admin chat
    # path("user/chat/rooms", ConversationView.as_view()),
    path("user/chat/message/<type>", MessageView.as_view()),
    # path("user/chat/participant", ParticipantView.as_view()),
    path("user/chat/delivered", DeliveredView.as_view()),
    path("user/chat/seen", SeenView.as_view()),
    path("user/chat/typing", TypingView.as_view()),
    path("user/chat/online", OnlineView.as_view()),
    path("user/chat/unread/messages", UnreadMessages.as_view()),

]
