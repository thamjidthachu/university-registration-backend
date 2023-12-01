from registration.views.admin.admission.ExcelExportReports.reportImports import *


class EnglishExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "EnglishReport"
                excel, query = report_columns_new([
                    'English Test Type',
                    'English Score',
                    'English Test Result',
                    'English Notes'
                ])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                       'Trial Number': 'test_try',
                                                                       'Confirmed': 'confirmed'
                                                            })
                condition = """ where  app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"}, status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
