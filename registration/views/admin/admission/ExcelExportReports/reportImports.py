from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN
from registration.views.admin.admission.ExcelExportReports.ReportBuilderClass import ReportBuilder,\
    get_user, query_tables, query_tables_less, report_columns_execlude, report_columns_new,\
    custom_columns_add, generate_dict, query_tables_equ
