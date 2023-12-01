from .reportImports import *


class PledgeFinalAccptedExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "PledgeFinalAccepted"
                excel, query = report_columns_execlude([
                    'Contact Result',
                    'Superior Number',
                    'Applicant Notes',
                    'English Notes'
                ])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                'Pledge': "case when pledge=True then 'Done' else 'Not' end "
                                                            })
                condition = """ where final_state = 'A' 
                                and   app.apply_semester = '{0}'
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
