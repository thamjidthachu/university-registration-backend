from .reportImports import *


class unCompletedApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "inCompleteApplicants"
                excel_cols, query_cols = report_columns_execlude([
                    'University ID',
                    'Initial State Date',
                    'Final State Date',
                    'Superior Number',
                    'Applicant Notes',
                    'English Notes',
                    'Interview Result',
                    'Interview Date',
                    'English Test Result',
                    'English State',
                    'English Test Type',
                    'Interview State',
                    'English Test Date',
                    'English Score',
                    'Applicant Type',
                    'Final State',
                    'Initial State'
                ])
                condition = """ where   init_state is null
                                 and    app.apply_semester = '{0}' 
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result
            return Response(
                {"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
