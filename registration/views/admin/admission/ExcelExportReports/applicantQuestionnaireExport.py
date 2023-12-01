from .reportImports import *


class applicantQuestionaireExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "applicant_questionaire"
                excel, query = report_columns_execlude([
                    'University ID',
                    'Superior Number',
                    'Applicant Notes',
                    'Contact Result',
                    'English Notes',
                ])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                        {
                            'The terms and conditions for registration were fair and clear': 'app.first_questionare',
                            'The registration process was smooth and easy': 'app.second_questionare'
                        })

                condition = """ where app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result
            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
