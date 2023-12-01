from registration.views.admin.admission.ExcelExportReports.reportImports import *


class CertifiedEnglishExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "CertifiedEnglishReport"
                excel, query = report_columns_new()
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                'Score': 'english_certf_score',
                                                                'Result': "case when english_certf_result ='S' then 'Succeeded' when english_certf_result ='L' then 'Low Score' when english_certf_result ='F' then 'Failed' when english_certf_result ='U' then 'Unknown Certificate' else NULL end"
                                                            })
                condition = """ where english_certf_score > 0 
                                 and  app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables_less
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"}, status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
