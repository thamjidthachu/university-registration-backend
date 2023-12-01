import json
import time
import urllib as lib
import urllib.request as urllib
from datetime import datetime

import cx_Oracle
import schedule


class saved_last:
    save_last = 0
    created = {}


def postRequest(saved):
    try:
        request = urllib.Request("https://my.um.edu.sa/backend/old/system/run", json.dumps(saved).encode("utf-8"))
        request.add_header('Content-Type', 'application/json; charset=utf-8')
        request.get_method = lambda: 'POST'
        urllib.urlopen(request)
    except lib.error.URLError as e:
        fn = open("log_old_system", "a+")
        fn.write(str(e.read()) + "\n<------------------------------------------------------------------------>\n")
        fn.close()


def getRequest():
    request = urllib.Request("https://my.um.edu.sa/backend/old/system/run")
    request.add_header('Content-Type', 'application/json; charset=utf-8')
    request.get_method = lambda: 'GET'
    return json.loads(urllib.urlopen(request).read())


def oldSystemRunAutomated():
    # count = getRequest()

    conn = cx_Oracle.connect("QABOOL_USER/QABOOL_USER@10.101.1.11:1521/ORCL", encoding="utf-8")
    cur = conn.cursor()
    list_national = ""
    if len(saved_last.created) > 0:
        list_national = "where national_id not in ("
        for i, l in enumerate(saved_last.created):
            list_national += "'{0}'".format("', '".join(saved_last.created[l]))  # ",".join(saved_last.created[l])
            if i != len(saved_last.created) - 1:
                list_national += ") and national_id not in ("
        list_national += ")"
    cur.execute(
        "select id,STUDENT_NAME_E,STUDENT_NAME_A, MOBILE_PHONE, EMAIL, GENDER, NATIONALITY_E, BIRTH_DATE, SEMESTER, NATIONAL_ID,QUDURAT, TAHSILI, UNIVERSITY_GPA, UNIVERSITY_YEAR, SCHOOL_AVG,NATIONALITY_A, SCHOOL_YEAR , SCHOOL_NAME,SCHOOL_CITY,REFERENCE_NAME,REFERENCE_MOBILE, TRANSFER_UNIVERSITY,PREV_UNIVERSITY, MAX_UNIVGPA from MCST.QABOOL_DATA  " + list_national)

    saved = []
    for item in cur:
        if saved_last.save_last in saved_last.created and len(saved_last.created[saved_last.save_last]) < 1000:
            if saved_last.save_last in saved_last.created:
                saved_last.created[saved_last.save_last].append(item[9])
            else:
                saved_last.created[saved_last.save_last] = [item[9]]
        else:
            saved_last.save_last += 1
            saved_last.created[saved_last.save_last] = [item[9]]
        if len(saved) == 5:
            postRequest(saved)
            saved = []

        data = {}

        data['full_name'] = item[1]
        data['arabic_full_name'] = item[2]
        data['phone'] = item[3]
        data['email'] = item[4]
        data['gender'] = "M" if item[5] == "Male" else "F"
        data['nationality'] = item[6]
        data['birth_date'] = datetime.strptime(item[7], '%d-%m-%Y').strftime('%Y-%m-%d')
        data['apply_semester'] = item[8]
        data['national_id'] = item[9]
        data['qudurat'] = item[10]
        data['tahsili'] = item[11]
        data['university_gpa'] = item[12]
        data['university_year'] = item[13]
        data['previous_gpa'] = item[14]
        data['nationality_arabic'] = item[15]
        data['high_school_year'] = item[16]
        data['high_school_name'] = item[17]
        data['high_school_city'] = item[18]
        data['reference_name'] = item[19]
        data['reference_phone'] = item[20]
        data['university_transfer'] = item[21]
        data['previous_university'] = item[22]
        data['max_prev_gpa'] = item[23]

        saved.append(data)

    if len(saved) > 0:
        postRequest(saved)


schedule.every(5).minutes.do(oldSystemRunAutomated)

while True:
    schedule.run_pending()
    time.sleep(1)
