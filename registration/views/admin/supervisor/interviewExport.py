from registration.views.admin.admission.ExcelExportReports.reportImports import *


class InterviewExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "applicantsInterviewReport"

                excel_cols, query_cols = report_columns_execlude([
                    'University ID',
                    'Family Name',
                    'Arabic Family Name',
                    'Nationality',
                    'Mother Nationality',
                    'Initial State Date',
                    'Final State Date',
                    'Superior Number',
                    'Contact Result',
                    'Applicant Notes',
                ])
                condition = """ where app.id in (select applicant_id_id from registration_interview)
                                 and  app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"}, status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
