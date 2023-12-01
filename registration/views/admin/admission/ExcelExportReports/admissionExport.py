from .reportImports import *


class ApplicantExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "applicants"

                excel, query = report_columns_execlude([
                    'Family Name',
                    'Arabic Family Name',
                    'Mother Nationality',
                    'Apply Semester',
                    'Initial State Date',
                    'Final State Date',
                    'Superior Number',
                    'Applicant Notes',
                    'English Notes',
                    'Interview State',
                    'Equation',
                    'Contact Result',
                ])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                # 'Offer': 'offer'
                                                                'Certificate Status': """case when app.certificate_status ='NS' then 'Not Submitted' when app.certificate_status ='PS' then 'Partially Submitted' when app.certificate_status ='FS' then 'Fully Submitted' else NULL end""",
                                                            })
                condition = """ where app.apply_semester = '{0}'"""

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)