import cx_Oracle
from registration.models.applicant import Applicant
import datetime


def updateGpa(obj=Applicant):
    conn = cx_Oracle.connect("QABOOL_USER/QABOOL_USER@10.101.1.11:1521/ORCL", encoding="utf-8")
    cur = conn.cursor()
    if cur:
        sql = 'update MCSTTEST.SIS_APPLICATIONS set SCHOOL_AVG = :high_school_GPA,UNIVERSITY_GPA=:previous_GPA where ' \
              'NATIONAL_ID=:NATIONAL_ID AND SEMESTER=:SEMESTER= '
        cur.execute(sql, high_school_GPA=obj.high_school_GPA, previous_GPA=obj.previous_GPA,
                           NATIONAL_ID=obj.national_id, SEMESTER=obj.apply_semester)
        conn.commit()
        conn.close()
