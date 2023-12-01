from .reportImports import *


class ApplicantFinalStateExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "applicants_final_state"

                excel, query = report_columns_execlude([
                    'Arabic Full Name',
                    'Family Name',
                    'Arabic Family Name',
                    'Mother Nationality',
                    'Initial State',
                    'Initial State Date',
                    'Apply Semester',
                    'Applicant Notes',
                    'English Notes',
                ])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                'Pledge': "case when pledge=True then 'Done' else 'Not' end "
                                                            })
                final = self.request.query_params['filter'] if 'filter' in self.request.query_params else None
                if not final:
                    condition = """ where app.apply_semester = '{0}']
                                    and app.final_state='A' 
                                                    """
                elif final == "student":
                    condition = """ where  app.final_state='A' 
                                     and   app.student_id is not null 
                                     and   app.apply_semester = '{0}']
                                """
                else:
                    condition = """ where app.apply_semester = '{0}'
                                    and   app.final_state='{1}'
                                """
                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        final, tables=query_tables
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"}, status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)