from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN
from .ReportBuilderClass import ReportBuilder, get_user, query_tables, report_columns_execlude


class nonReservedInterviewApplicantsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "unReservedInterviewApplicants"

                excel_cols, query_cols = report_columns_execlude([
                                'University ID',
                                'Initial State Date',
                                'Final State Date',
                                'Superior Number',
                                'Interview Result',
                                'Interview Date',
                                'Interview State',
                                'Applicant Notes',
                                'Contact Result',
                ])
                condition = """ where app.id in (select applicant_id_id from registration_englishtest where confirmed = true) 
                                 and  app.id not in (select applicant_id_id from registration_interview)  
                                 and  app.apply_semester = '{0}'
                            """

                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result
            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)