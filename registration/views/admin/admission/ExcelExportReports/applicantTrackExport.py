from .reportImports import *


class applicantTrackExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "applicants"
                basic_elements = [
                    'National ID',
                    'Full Name',
                    'Email',
                    'Registration Date',
                    'Initial State',
                    'Initial State Date'
                ]
                new_elements = [
                    'Final State',
                    'Final State Date'
                ]
                excel, query = report_columns_new(new_elements, basic_elements)
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                'Admission User Name': "us." + '"{}"'.format('userName'),
                                                                'Admission Phone': "us." + '"{}"'.format('Phone'),
                                                                'Admission Email': 'us.email',
                                                                'Admission Role': 'us.role'
                                                            })

                condition = """ where  app.apply_semester = '{0}'
                                 order by app.id
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=track_tables
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)


def track_tables():
    return """ from registration_applicant app
               left join registration_major maj 
               on app.major_id_id = maj.id
               left join registration_user us
               on us.id=app.modified_user_id
            """


'''
'File Name': 'file_name',
'File Status': 'file.status',
'Reject Reason': 'rej_reason',
'Modified User': "file_us."+'"{}"'.format('userName'),
'File Update Date': 'cast(file.modify_user as date)'

left join registration_files file
on file.applicant_id_id = app.id
left join registration_user file_us
on file.user_id = file_us.id
'''
