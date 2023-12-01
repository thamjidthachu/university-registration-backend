from .reportImports import *


class absentInterviewApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "AbsentInterviewApplicants"
                excel_cols, query_cols = report_columns_execlude([
                    'University ID',
                    'Initial State Date',
                    'Final State Date',
                    'Superior Number',
                    'English State',
                    'English Score',
                    'English Test Result',
                    'English Test Type',
                    'Interview Result',
                    'Interview State',
                    'English Test Date',
                    'Contact Result',
                    'Applicant Notes',
                    'English Notes'
                ])
                condition = """ where app.id in (select applicant_id_id from registration_absent)
                                and  interview_res.id in (select reservation_id_id from registration_absent)
                                and  app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result
            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"}, status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
