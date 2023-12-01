from .reportImports import *


class ContactCountsExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "counts"

                columns = ['أفاد بالحضور', 'لم يتم الرد', 'تم الانسحاب من التسجيل', 'الراغبون فى تخصص الطب']

                query_cols = """  count(case when contact_result='WA' then 1 end ),
                                  count(case when contact_result='NR' then 1 end ),
                                  count(case when contact_result='WR' then 1 end ),  
                                  count(case when contact_result='MM' then 1 end )
                             """

                condition = " where app.apply_semester = '{0}'"

                result = report.create_report_structure(file_name, columns, query_cols, condition,
                                                        str(self.request.query_params['semester']),
                                                        tables=query_tables
                                                        )
                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)
