from registration.views.admin.admission.ExcelExportReports.reportImports import *
from registration.models.univStructure import Major


class deanApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            user = get_user(self.request.query_params['id'])
            user_role = user.last().role
            if user.exists() and user_role in (2, 7, 9, 10):
                if user_role == 7:
                    dean_faculty = "PH"
                elif user_role == 9:
                    dean_faculty = "M"
                else:
                    dean_faculty = "AS"

                dean = Major.objects.filter(faculty_id__name=dean_faculty).values('id')
                file_name = "applicants"

                excel, query = report_columns_execlude([
                    'University ID',
                    'Apply Semester',
                    'Superior Number',
                    'English Test Type',
                    'Contact Result',
                    'Applicant Notes',
                    'English Notes'
                ])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                'Offer': 'offer'
                                                            })
                if len(list(dean)) == 1:
                    one_major = list(dean)[0]['id']
                    condition = """ where app.major_id_id in ({0}) 
                                    and   app.apply_semester = '{1}'
                                """
                    result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                            str(one_major),
                                                            str(self.request.query_params['semester']),
                                                            tables=query_tables
                                                            )
                else:
                    majors_list = []
                    for index, item in enumerate(list(dean)):
                        majors_list.append(item['id'])
                    majors_group = tuple(majors_list)
                    condition = """ where app.major_id_id in {0} 
                                    and   app.apply_semester = '{1}'
                                """
                    result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                            str(majors_group),
                                                            str(self.request.query_params['semester']),
                                                            tables=query_tables
                                                            )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
