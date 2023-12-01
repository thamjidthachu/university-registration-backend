import cx_Oracle
from registration.models.applicant import Applicant
from django.db import connection
import datetime


def update_GPA_QUDRAT_TAHSILY(obj=Applicant):
    conn = cx_Oracle.connect("QABOOL_USER/QABOOL_USER@10.101.1.11:1521/ORCL", encoding="utf-8")
    qabool_cur = conn.cursor()
    if qabool_cur:
        sql = 'select PROCESS_ID from MCSTTEST.SIS_APPLICATIONS where NATIONAL_ID=:NATIONAL_ID AND SEMESTER=:SEMESTER'
        qabool_cur.execute(sql, semester=obj.apply_semester, NATIONAL_ID=obj.national_id)
        result = qabool_cur.fetchone()
        if result is None:
            PROCESS_ID = None
        else:
            PROCESS_ID = result[0]

        entry_date = f"{datetime.datetime.now():%d-%b-%y}"

        sql1 = 'update MCSTTEST.SIS_APPLICATIONS set SCHOOL_AVG = :high_school_GPA,UNIVERSITY_GPA=:previous_GPA where NATIONAL_ID=:NATIONAL_ID AND SEMESTER=:SEMESTER'
        qabool_cur.execute(sql1, high_school_GPA=obj.high_school_GPA, previous_GPA=obj.previous_GPA,
                           NATIONAL_ID=obj.national_id, SEMESTER=obj.apply_semester)
        conn.commit()

        ''' Update Qudrat '''
        sql2 = 'update MCSTTEST.SIS_ADMINEXAM_MARKS set MARK = :MARK,LAST_UPDATE_DATE=:last_date  where PROCESS_ID=:PROCESS_ID AND SEMESTER=:SEMESTER AND EXAM_CODE=1'
        qabool_cur.execute(sql2, MARK=obj.qiyas_aptitude, last_date=entry_date, PROCESS_ID=PROCESS_ID,
                           SEMESTER=obj.apply_semester)
        conn.commit()

        ''' Update Tahsily '''
        sql3 = 'update MCSTTEST.SIS_ADMINEXAM_MARKS set MARK = :MARK,LAST_UPDATE_DATE=:last_date  where PROCESS_ID=:PROCESS_ID AND SEMESTER=:SEMESTER AND EXAM_CODE=2'
        qabool_cur.execute(sql3, MARK=obj.qiyas_achievement, last_date=entry_date, PROCESS_ID=PROCESS_ID,
                           SEMESTER=obj.apply_semester)
        conn.commit()

        conn.close()

    else:
        raise Exception("Conncetion Error")


def get_major(appID):
    mcst_cur = connection.cursor()
    mcst_cur.execute('select case when name = \'MS\' then 1 \
                                  when name = \'PHD\' then 2 \
                                  when name = \'NU\' then 3 \
                                  when name = \'RT\' then 4 \
                                  when name = \'CS\' then 5 \
                                  when name = \'IS\' then 6 \
                                  when name = \'EMS\' then 7 \
                                  when name = \'IE\' then 8 \
                                  when name = \'IE\' then 9 \
                                  when name = \'HIS\' then 10 \
                                  else 1 \
                        end from "registration_applicant" app JOIN "registration_major" maj ON maj.id = app.major_id_id where app."national_id"=%s',
                     [appID])
    result = mcst_cur.fetchone()
    if result is not None:
        major = result[0]
    else:
        major = None
    return major


def update_major(obj=Applicant):
    conn = cx_Oracle.connect("QABOOL_USER/QABOOL_USER@10.101.1.11:1521/ORCL", encoding="utf-8")
    qabool_cur = conn.cursor()
    if qabool_cur:
        major = get_major(obj.national_id)

        sql = 'select PROCESS_ID from MCSTTEST.SIS_APPLICATIONS where NATIONAL_ID=:NATIONAL_ID AND SEMESTER=:SEMESTER'
        qabool_cur.execute(sql, semester=obj.apply_semester, NATIONAL_ID=obj.national_id)
        result = qabool_cur.fetchone()
        if result is None:
            PROCESS_ID = None
        else:
            PROCESS_ID = result[0]

        sql2 = 'update MCSTTEST.SIS_APPLICATION_CHOICES set CHOICE = :CHOICE where PROCESS_ID=:PROCESS_ID AND SEMESTER=:SEMESTER'
        qabool_cur.execute(sql2, CHOICE=major, PROCESS_ID=PROCESS_ID, SEMESTER=obj.apply_semester)
        conn.commit()

        conn.close()

    else:
        raise Exception("Conncetion Error")
