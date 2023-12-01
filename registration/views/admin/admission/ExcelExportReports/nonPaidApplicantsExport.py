from .reportImports import *


class nonPaidApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "notPaidApplicants"
                excel_cols, query_cols = report_columns_execlude([
                    'Initial State Date',
                    'Final State Date',
                    'English Test Type',
                    'English State',
                    'English Test Date',
                    'English Test Type',
                    'Interview State',
                    'Interview Result',
                    'Interview Date'
                ])
                condition = """ where (offer= 'AC' or final_state= 'A') 
                                 and   accepted_outside = false 
                                 and   app.id not in (select applicant_id_id from registration_payment where paid = true and payment_id_id in (select id from registration_univpayments where payment_title = 'REG') )
                                 and   app.apply_semester = '{0}'"""

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"}, status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)