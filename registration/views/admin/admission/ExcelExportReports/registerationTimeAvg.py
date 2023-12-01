from .reportImports import *


class registerationTimeAverageExportXlsx(GenericAPIView):
    def get(self,request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "registeration_time_average"
                excel, query = report_columns_execlude([
                    'Initial State',
                    'Final State',
                    'Qudrat',
                    'Tahsily',
                    'Sat',
                    'Family Name',	
                    'Arabic Family Name',
                    'Mother Nationality',
                    'High School GPA',
                    'previous GPA',
                    'Superior Number',
                    'Apply Semester',
                    'Initial State Date',
                    'English Test Date',
                    'English State',
                    'English Test Type',
                    'English Score',  
                    'English Test Result',  
                    'Interview State',  
                    'Interview Result', 
                    'Interview Date', 
                    'Contact Result',
                    'Applicant Type',
                    'Equation', 
                    'Applicant Notes',
                    'English Notes'
                ])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                            {
                                                'Registeration Duration / Days' :    "cast(app.final_state_date as date) - cast(app.registration_date as date)"
                                            })
                
                condition = """ where student_id is not null 
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