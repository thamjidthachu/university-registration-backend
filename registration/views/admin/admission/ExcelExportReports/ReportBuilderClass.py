from django.http import HttpResponse
from registration.models.user_model import User
from django.db import connection
import xlwt
from registration.models.applicant import INIT_STAT_CHOICES, FINAL_STAT_CHOICES, APPLY_CHOICES, CONTACT_RESULTS, \
    OFFER_CHOICES, FILE_STAT_CHOICES
from registration.models.evaluation import RES_CHOICES
from registration.models.univStructure import MAJOR_CHOICES
import datetime

columns = {
    'Sl. No': 'ROW_NUMBER() OVER (ORDER BY app.id) AS serial_number',
    'University ID': 'student_id',
    'Full Name': 'app.full_name',
    'Arabic Full Name': 'arabic_full_name',
    'National ID': 'national_id',
    'Family Name': 'family_name',
    'Arabic Family Name': 'arabic_family_name',
    'Email': 'app.email',
    'Phone No': 'phone',
    'Gender': 'app.gender',
    'Nationality': 'nationality',
    'Mother Nationality': 'mother_nationality',
    'Major': 'maj.name',
    'High School GPA': '"{}"'.format('high_school_GPA'),
    'Qudrat': 'qiyas_aptitude',
    'Tahsily': 'qiyas_achievement',
    'Sat': 'sat_score',
    'Registration Date': 'cast(app.registration_date as date)',
    'Initial State': "init_state",
    'Initial State Date': 'cast(app.init_state_date as date)',
    'Apply Semester': 'app.apply_semester',
    'Superior Number': 'superior_phone',
    'Applicant Type': "applicant_type",
    'University Information': 'previous_university',
    'previous GPA': 'case when "{}" <> 0 then "{}" else NULL end'.format('previous_GPA', 'previous_GPA'),
    'English State': "case when eng.applicant_id_id is null and app.english_certf_result is NULL then 'Not Reached' "
                     "when app.english_certf_result is not NULL and app.english_certf_result = 'S' then 'Certified' "
                     "else 'University Tested' end",
    'English Test Type': "case when eng.test_type ='OX' then 'Oxford' when eng.test_type ='T' then 'TOEFL' when "
                         "eng.test_type ='I' then 'ILETS' when eng.test_type = 'S' then 'STEP' else NULL  end",
    'English Score': "case when eng.applicant_id_id is not null then eng.score when app.english_certf_result is not "
                     "NULL and app.english_certf_score <> 0 then app.english_certf_score else null end",
    'English Test Date': "english_res.reservation_date+english_res.start_time",
    'English Test Result': "case when (app.english_certf_result is not NULL and app.english_certf_result = 'S') then "
                           "english_certf_result else eng.result end",
    'Interview State': "(case when int.applicant_id_id is null then 'Not Reached' else 'Done' end)",
    'Interview Date': 'interview_res.reservation_date+interview_res.start_time',
    'Interview Result': 'int.result',
    'Equation': 'equation',
    'Contact Result': 'contact_result',
    'Applicant Notes': 'app.notes',
    'English Notes': 'eng.notes',
    'Final State': "final_state",
    'Final State Date': 'cast(app.final_state_date as date)',
    'Percentage': """ CASE WHEN "high_school_GPA" IS NOT NULL AND qiyas_aptitude IS NOT NULL AND qiyas_achievement IS NOT NULL
              THEN CAST(("high_school_GPA" * 0.3 + qiyas_aptitude * 0.3 + qiyas_achievement * 0.4)
              AS DECIMAL(10,2))
              ELSE NULL END """,
   
}


class ReportBuilder:
    def __init__(self, *args, **kwargs):
        self.cursor = connection.cursor()

        self.font_style = xlwt.XFStyle()
        self.font_style.font.bold = True

        self.dateStyle = xlwt.XFStyle()
        self.dateStyle.num_format_str = 'DD-MM-YY'
        self.dateStyle.font.bold = True

        self.TimeStampStyle = xlwt.XFStyle()
        self.TimeStampStyle.num_format_str = 'DD-MM-YY HH:MM'
        self.TimeStampStyle.font.bold = True

    def foramt_columns(self, ws, excel_cols, rows):
        row_num = 0
        for row in rows:
            row_num += 1
            for col in range(len(row)):

                if 'Gender' in excel_cols and col == excel_cols.index('Gender') and row[col]:
                    if row[col] == 'M':
                        gender = 'Male'
                    else:
                        gender = 'Female'
                    ws.write(row_num, col, gender, self.font_style)

                elif 'Initial State' in excel_cols and col == excel_cols.index('Initial State') and row[col]:
                    ws.write(row_num, col, dict(INIT_STAT_CHOICES)[row[col]], self.font_style)

                elif 'Final State' in excel_cols and col == excel_cols.index('Final State') and row[col]:
                    ws.write(row_num, col, dict(FINAL_STAT_CHOICES)[row[col]], self.font_style)

                elif 'Offer' in excel_cols and col == excel_cols.index('Offer') and row[col]:
                    ws.write(row_num, col, dict(OFFER_CHOICES)[row[col]], self.font_style)

                elif 'Major' in excel_cols and col == excel_cols.index('Major') and row[col]:
                    ws.write(row_num, col, dict(MAJOR_CHOICES)[row[col]], self.font_style)

                elif 'Registration Date' in excel_cols and col == excel_cols.index('Registration Date') and row[col]:
                    ws.write(row_num, col, row[col], self.dateStyle)

                elif 'Initial State Date' in excel_cols and col == excel_cols.index('Initial State Date') and row[col]:
                    ws.write(row_num, col, row[col], self.dateStyle)

                elif 'Final State Date' in excel_cols and col == excel_cols.index('Final State Date') and row[col]:
                    ws.write(row_num, col, row[col], self.dateStyle)

                elif 'English Test Date' in excel_cols and col == excel_cols.index('English Test Date') and row[col]:
                    ws.write(row_num, col, row[col], self.TimeStampStyle)

                elif 'Interview Date' in excel_cols and col == excel_cols.index('Interview Date') and row[col]:
                    ws.write(row_num, col, row[col], self.TimeStampStyle)

                elif 'English Test Result' in excel_cols and col == excel_cols.index('English Test Result') and row[
                    col]:
                    ws.write(row_num, col, dict(RES_CHOICES)[row[col]], self.font_style)

                elif 'Interview Result' in excel_cols and col == excel_cols.index('Interview Result') and row[col]:
                    ws.write(row_num, col, dict(RES_CHOICES)[row[col]], self.font_style)

                elif 'Applicant Type' in excel_cols and col == excel_cols.index('Applicant Type') and row[col]:
                    ws.write(row_num, col, dict(APPLY_CHOICES)[row[col]], self.font_style)

                elif 'Contact Result' in excel_cols and col == excel_cols.index('Contact Result') and row[col]:
                    ws.write(row_num, col, dict(CONTACT_RESULTS)[row[col]], self.font_style)

                elif 'Payment Date' in excel_cols and col == excel_cols.index('Payment Date') and row[col]:
                    ws.write(row_num, col, row[col], self.dateStyle)

                elif 'File Update Date' in excel_cols and col == excel_cols.index('File Update Date') and row[col]:
                    ws.write(row_num, col, row[col], self.dateStyle)

                elif 'Admission Role' in excel_cols and col == excel_cols.index('Admission Role') and row[col]:
                    ws.write(row_num, col, dict(User.USER_ROLES)[row[col]], self.font_style)

                elif 'Equation Date' in excel_cols and col == excel_cols.index('Equation Date') and row[col]:
                    ws.write(row_num, col,
                             row[col].strftime("%Y-%m-%d") if isinstance(row[col], datetime.datetime) else row[col],
                             self.dateStyle)

                else:
                    ws.write(row_num, col, row[col], self.font_style)

    def create_report_structure(self, file_name, excel_cols, query_columns, sql_condition,
                                *sql_condition_variables, **query_table):

        res = HttpResponse(content_type='application/ms-excel')
        res['Content-Disposition'] = 'attachment; filename=' + file_name + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Applicant Data')
        ws.row(0).height = 60 * 10
        long_cols = ['Full Name', 'Arabic Full Name', 'Applicant Notes', 'English Notes',
                     'The terms and conditions for registration were fair and clear',
                     'The registration process was smooth and easy']
        for ele in excel_cols:
            if ele not in long_cols:
                ws.col(excel_cols.index(ele)).width = 200 * 30
            else:
                ws.col(excel_cols.index(ele)).width = 500 * 30
        for col in range(len(excel_cols)):
            ws.write(0, col, excel_cols[col], self.font_style)

        if sql_condition is None:
            query = "select " + query_columns + query_table['tables']()
        else:
            query = "select " + query_columns + query_table['tables']() + sql_condition.format(*sql_condition_variables)

        self.cursor.execute(query)
        self.foramt_columns(ws, excel_cols, self.cursor.fetchall())
        wb.save(res)
        return res


def report_columns_execlude(execluded_elements=None):
    if execluded_elements is None:
        execluded_elements = []
    ex_cols = [element for element in columns if element not in execluded_elements]
    query_cols = ','.join([val for key, val in columns.items() if key not in execluded_elements])
    return ex_cols, query_cols


def report_columns_new(new_elements=None, basic_elements=None):
    if new_elements is None:
        new_elements = []
    if basic_elements is None:
        basic_elements = [
            'National ID',
            'Full Name',
            'Arabic Full Name',
            'Email',
            'Phone No',
            'Gender',
            'Initial State',
            'Final State',
            'Major',
            'Registration Date',
            'Qudrat',
            'Tahsily',
            'High School GPA',
            'previous GPA'
        ]
    for ele in new_elements:
        basic_elements.append(ele)
    new_col_list = list(set(basic_elements))
    excel_cols = [element for element in columns if element in new_col_list]
    query_cols = ','.join([val for key, val in columns.items() if key in new_col_list])
    return excel_cols, query_cols


def custom_columns_add(cols, new_col_dict):
    cols.update(new_col_dict)
    ex_cols = [element for element in cols]
    query_cols = ','.join([val for key, val in cols.items()])
    return ex_cols, query_cols


#old function
# def generate_dict(excel, query):
#     return dict(zip(excel, query.split(",")))

def generate_dict(excel, query):
    placeholder = "###DECIMAL_PLACEHOLDER###"
    query_placeholder = query.replace("DECIMAL(10,2)", placeholder)
    query_columns = query_placeholder.split(",")
    
    query_columns = [part.replace(placeholder, "DECIMAL(10,2)") for part in query_columns]
    
    return dict(zip(excel, query_columns))


# Alternate Method : here the comma between is getting splited DECIMAL(10,2) for applicant report total Gpa field
# def generate_dict_for_total_gpa(excel, query):
#     placeholder = "###DECIMAL_PLACEHOLDER###"
#     query_placeholder = query.replace("DECIMAL(10,2)", placeholder)
#     query_columns = query_placeholder.split(",")
    
#     query_columns = [part.replace(placeholder, "DECIMAL(10,2)") for part in query_columns]
    
#     return dict(zip(excel, query_columns))


def query_tables():
    return """ 
            from registration_applicant app
            LEFT JOIN
            (
                SELECT applicant_id_id, MAX(score) AS score
                FROM registration_englishtest
                GROUP BY applicant_id_id
            ) max_eng ON app.id = max_eng.applicant_id_id
            left join registration_englishtest eng 
            on app.id = eng.applicant_id_id AND eng.score = max_eng.score AND ((eng.test_try = 1 AND eng.result = 'S') OR (eng.test_try = 2))
            left join registration_interview int 
            on app.id = int.applicant_id_id
            left join registration_reservation english_res 
            on eng.reservation_id_id = english_res.id
            left join registration_reservation interview_res 
            on int.reservation_id_id = interview_res.id
            left join registration_major maj 
            on app.major_id_id = maj.id
            """


def query_tables_less():
    return """ from registration_applicant app 
               left join registration_major maj 
               on app.major_id_id = maj.id """


def query_tables_equ():
    return """ from registration_applicant app
                LEFT JOIN
                (
                    SELECT applicant_id_id, MAX(score) AS score
                    FROM registration_englishtest
                    GROUP BY applicant_id_id
                ) max_eng ON app.id = max_eng.applicant_id_id
                left join registration_englishtest eng 
                on app.id = eng.applicant_id_id AND eng.score = max_eng.score AND ((eng.test_try = 1 AND eng.result = 'S') OR (eng.test_try = 2))
                left join registration_interview int 
                on app.id = int.applicant_id_id
                left join registration_reservation english_res 
                on eng.reservation_id_id = english_res.id
                left join registration_reservation interview_res 
                on int.reservation_id_id = interview_res.id
                left join registration_major maj 
                on app.major_id_id = maj.id
                left join equations_equation equ
                on app.id = equ.applicant_id
                """


def get_user(user_id):
    return User.objects.filter(id=user_id)
