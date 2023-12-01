from .reportImports import *


class noResultInterviewApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "noResultInterviewApplicants"
                excel_cols, query_cols = report_columns_execlude([
                    'University ID',
                    'Initial State Date',
                    'Final State Date',
                    'Superior Number',
                    'Applicant Notes',
                    'English Notes',
                    'Interview Result',
                    'English Test Result',
                    'English Test Type',
                    'English Test Date',
                    'Interview State',
                    'English State',
                    'English Score',
                    'Contact Result'
                ])
                condition = """ where   app.id in (select applicant_id_id from registration_interview where result is null ) 
                                 and    app.apply_semester = '{0}' 
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result
            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
