from .reportImports import *


class nonReservedEnglishApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "unReservedEnglishDates"
                excel_cols, query_cols = report_columns_execlude([
                    'University ID',
                    'Final State Date',
                    'Superior Number',
                    'English Score',
                    'English State',
                    'Interview State',
                    'English Test Date',
                    'English Test Result',
                    'English Test Type',
                    'Interview Result',
                    'Interview Date',
                    'Applicant Notes',
                    'Contact Result',
                    'English Notes',
                ])
                condition = """ where init_state in ('IA','CA') 
                                 and  app.english_certf_score = 0
                                 and  app.id not in (select applicant_id_id from registration_englishtest) 
                                 and  app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result
            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
