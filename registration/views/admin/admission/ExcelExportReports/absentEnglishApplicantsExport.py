from .reportImports import *


class absentEnglishApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "AbsentEnglishApplicants"
                excel_cols, query_cols = report_columns_execlude([
                    'University ID',
                    'Initial State Date',
                    'Final State Date',
                    'Superior Number',
                    'English Score',
                    'English Test Result',
                    'English Test Type',
                    'English State',
                    'Interview State',
                    'Interview Result',
                    'Interview Date',
                    'Contact Result',
                    'Applicant Notes',
                    'English Notes'
                ])
                condition = """ where app.id in (select applicant_id_id from registration_absent)
                                and  english_res.id in (select reservation_id_id from registration_absent)
                                and  app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=english_tables
                                                        )
                return result
            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)


def english_tables():
    return """ from registration_applicant app
               left join registration_englishtest eng 
               on app.id = eng.applicant_id_id
               left join registration_reservation english_res 
               on eng.reservation_id_id = english_res.id
               left join registration_major maj 
               on app.major_id_id = maj.id
            """
