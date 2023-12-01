from registration.views.admin.admission.ExcelExportReports.reportImports import *
from registration.models.univStructure import Major


class EquationsReport(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            user = get_user(self.request.query_params['id'])
            if user.exists():
                file_name = "EquationsReport"
                basic_elements = ['Sl. No', 'University ID', 'National ID', 'Full Name', 'Arabic Full Name', 'Email', 'Phone No',
                                  'Gender', 'Major']
                excel, query = report_columns_new(basic_elements=basic_elements)
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                'University ID': "case when student_id is not null then student_id else 'Not generated yet' end",
                                                                'Equation Date': 'equ.created',
                                                                'Equation Supervisor Status': "case when equ.init_state ='AC' then 'Accepted' when equ.init_state ='RJ' then 'Rejected' when equ.init_state ='NM' then 'Need Modification' when equ.init_state ='UR' then 'Under Review' when equ.init_state ='IA' then 'Initial Acceptance' else NULL end",
                                                                'Head Of Department Status': "case when equ.head_of_department_state ='AC' then 'Accepted' when equ.head_of_department_state ='RJ' then 'Rejected' else NULL end",
                                                                'Dean Status': "case when equ.final_state ='AC' then 'Accepted' when equ.final_state ='RJ' then 'Rejected' when equ.final_state ='NM' then 'Need Modification' when equ.final_state ='UR' then 'Under Review' when equ.final_state ='IA' then 'Initial Acceptance' else NULL end",
                                                                'Confirmed': "case when equ.confirmed =True then 'Yes' else 'No' end",
                                                            })

                if user.last().role in [7, 9, 10]:
                    role = user.last().role
                    dean_faculty = "PH" if role == 7 else "M" if role == 9 else "AS"

                    dean = Major.objects.filter(faculty_id__name=dean_faculty).values('id')
                    if len(list(dean)) == 1:
                        one_major = list(dean)[0]['id']
                        condition = """ where app.major_id_id in ({0}) 
                                        and   app.apply_semester = '{1}'
                                    """
                        result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                                str(one_major),
                                                                str(self.request.query_params['semester']),
                                                                tables=query_tables_equ
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
                                                                tables=query_tables_equ
                                                                )
                    return result
                condition = """ where app.apply_semester = '{0}'"""

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables_equ
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
