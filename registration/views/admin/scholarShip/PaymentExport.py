from registration.views.admin.admission.ExcelExportReports.reportImports import *


class PaymentExportXlsx(GenericAPIView):
    def get(self, request):
        if {'id', 'semester'} <= self.request.query_params.keys():
            report = ReportBuilder()
            admission = get_user(self.request.query_params['id'])
            if admission.exists():
                file_name = "applicantPayments"
                excel, query = report_columns_new(['University ID'])
                excel_cols, query_cols = custom_columns_add(generate_dict(excel, query),
                                                            {
                                                                'Card Number': 'pay.card_number',
                                                                'Payment Date': "cast(payment_date as date)",
                                                                'Payment Type': "case when payment_title ='ERET' then 'English Retest Fees' when payment_title ='EQU' Then 'Equation Fees' else 'Registration Fees' end",
                                                                'Payment Cost': "case when left(national_id,1) <> '1' then amount - amount*.15 else amount end",
                                                                'VAT $': "case when left(national_id,1) <> '1' then amount*.15 else 0 end ",
                                                                'Paid Amount': "amount"
                                                            })
                condition = """ where paid = TRUE 
                                and  app.apply_semester = '{0}'
                            """
                result = report.create_report_structure(file_name, excel_cols, query_cols, condition,
                                                        str(request.query_params['semester']),
                                                        tables=payment_tables
                                                        )

                return result

            return Response({"Error": "Unauthorized to access this link!", "Error_ar": "غير مسموح بالوصول لهذا الرابط"},
                            status=HTTP_403_FORBIDDEN)

        return Response({"Error": "ERROR IN REQUEST!", "Error_ar": "خطأ فى الإتصال"}, status=HTTP_403_FORBIDDEN)


def payment_tables():
    return """
           from registration_applicant app  
           left join registration_major maj 
           on app.major_id_id = maj.id 
           left join registration_payment pay 
           on pay.applicant_id_id = app.id     
           left join registration_univpayments univ 
           on univ.id = pay.payment_id_id  
           """
