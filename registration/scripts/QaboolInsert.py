import cx_Oracle
from registration.models.applicant import Applicant
from django.db import connection
import datetime


def get_data(obj: Applicant) -> dict:
    return_data = {}

    mcst_cur = connection.cursor()
    mcst_cur.execute(
        'select sch."Country_no",sch."School_no",sch."city_id" from "registration_school" as sch JOIN "registration_applicant" as app ON sch."School_name" =app."high_school_name" JOIN "registration_city" as cit ON cit."id"=sch."city_id"  where app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        school_country = result[0]
        school_code = result[1]
        school_city = result[2]
    else:
        school_country = None
        school_code = None
        school_city = None

    entry_date = f"{datetime.datetime.now():%d-%b-%y}"

    mcst_cur.execute(
        'select case when gender = \'M\' then 1 else 2 end from "registration_applicant" as app where app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        gender = result[0]
    else:
        gender = None

    # when name = \'GSE\' then 11 \
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
                        end from "registration_applicant" app JOIN "registration_major" maj ON maj.id = app.major_id_id where app."id"=%s',
                     [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        major = result[0]
    else:
        major = None

    mcst_cur.execute(
        'select case when employment_state = \'work\' then 1 else 0 end from "registration_applicant" as app where app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        employ = result[0]
    else:
        employ = None

    mcst_cur.execute(
        'select case when final_state is null then 0 else 1 end from "registration_applicant" as app where app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        approval_status = result[0]
    else:
        approval_status = None

    mcst_cur.execute(
        'select case when "tagseer_GPA" is null then 0 else 1 end from "registration_applicant" as app where app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        is_pred = result[0]
    else:
        is_pred = None

    mcst_cur.execute(
        'select uni."country_id" from "registration_university" as uni,"registration_applicant" as app where (uni."arabic_name" =app."previous_university" or uni."name" =app."previous_university") and app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        univ_country = result[0]
    else:
        univ_country = None

    mcst_cur.execute(
        'select nat."Country_no" from "registration_nationality" as nat,"registration_applicant" as app where (nat."nationality" =app."nationality" or nat."arabic_nationality" = app."nationality")  and app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        country_code = result[0]
    else:
        country_code = None

    mcst_cur.execute(
        'select nat."Country_no" from "registration_nationality" as nat,"registration_applicant" as app where (nat."nationality" =app."mother_nationality" or nat."arabic_nationality" = app."mother_nationality") and app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        mother_country_code = result[0]
    else:
        mother_country_code = None

    mcst_cur.execute(
        'select nat."Country_no" from "registration_nationality" as nat,"registration_applicant" as app where (nat."nationality" =app."mother_nationality" or nat."arabic_nationality" = app."mother_nationality")  and app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        considered_nationality = result[0]
    else:
        considered_nationality = None

    mcst_cur.execute(
        'select cit."City_no" from "registration_city" as cit,"registration_applicant" as app where cit."arabic_city_name" =app."city"  and app."id"=%s',
        [obj.id])
    result = mcst_cur.fetchone()
    if result is not None:
        city = result[0]
    else:
        city = None

    mcst_cur.execute('select cit."zone_code" \
                    from \
                    "registration_school" as sch \
                    JOIN "registration_city" as cit \
                    ON cit."id" = sch."city_id" \
                    JOIN "registration_applicant" as app \
                    ON sch."School_name" =app."high_school_name" \
                    where app."id"=%s', [obj.id])

    result = mcst_cur.fetchone()
    if result is not None:
        school_zone = result[0]
    else:
        school_zone = None
    if obj.building_no is not None and obj.street_no is not None and obj.district is not None and obj.city is not None and obj.nationality is not None:
        address = obj.building_no + ' ' + obj.street_no + ' ' + obj.district + ' ' + obj.city + ' ' + obj.nationality
    else:
        address = None
    return_data.update({
        'school_country': school_country, 'school_code': school_code, 'school_city': school_city,
        'entry_date': entry_date,
        'gender': gender, 'employ': employ, 'univ_country': univ_country, 'country_code': country_code,
        'mother_country_code': mother_country_code,
        'considered_nationality': considered_nationality, 'city': city, 'school_zone': school_zone,
        'apply_semester': obj.apply_semester,
        'national_id': obj.national_id, 'arabic_first_name': obj.arabic_first_name,
        'arabic_middle_name': obj.arabic_middle_name,
        'arabic_last_name': obj.arabic_last_name, 'first_name': obj.first_name, 'middle_name': obj.middle_name,
        'is_pred': is_pred,
        'last_name': obj.last_name, 'high_school_GPA': obj.high_school_GPA, 'high_school_year': obj.high_school_year,
        'last_semester': obj.last_semester, 'previous_GPA': obj.previous_GPA, 'birth_date': obj.birth_date,
        'superior_arabic_name': obj.superior_arabic_name, 'superior_name': obj.superior_name, 'email': obj.email,
        'home_phone': obj.home_phone, 'max_gpa': obj.max_gpa, 'phone': obj.phone,
        'high_graduation_year': obj.high_graduation_year,
        'postal_code': obj.postal_code, 'previous_university': obj.previous_university,
        'registration_date': obj.registration_date, 'birth_place': obj.birth_place,
        'qudrat': obj.qiyas_aptitude, 'tahsily': obj.qiyas_achievement, 'approval_status': approval_status,
        'major': major,
        'ref_name': obj.superior_arabic_name, 'ref_phone': obj.superior_phone,
        'ref_national_id': obj.superior_nationalID, 'ref_relation': obj.superior_relation,
        'marital_status': obj.marital_status, 'family_name': obj.family_name,
        'arabic_family_name': obj.arabic_family_name,
        'street_no': obj.street_no, 'address': address,
        'building_no': obj.building_no, 'city_name': obj.city, 'district': obj.district
    })
    return return_data


def insertApplicant(data):
    conn = cx_Oracle.connect("QABOOL_USER/QABOOL_USER@10.101.1.11:1521/ORCL", encoding="utf-8")
    qabool_cur = conn.cursor()

    if qabool_cur:
        query = 'select max(process_id) from mcsttest.sis_applications where SEMESTER = :semester group by ("SEMESTER")  '
        qabool_cur.execute(query, semester=int(data['apply_semester']))
        result = qabool_cur.fetchone()
        if result is None:
            new_id = 1
        else:
            new_id = result[0] + 1
        '''
        query='select CITY_NO from mcsttest.gen_cities where CITY_NAME = :CITY_NAME '
        qabool_cur.execute(query,CITY_NAME=data['city'])
        result=qabool_cur.fetchone()
        if result is not None :
            PERM_CITY =result[0]
            BIRTH_CITY=result[0]
            LIVING_CITY = result[0]
        else:
            PERM_CITY = None
            BIRTH_CITY=None
            LIVING_CITY=None

        query='select CITY_NO from mcsttest.gen_cities where CITY_NAME = :SCHOOL_CITY '
        qabool_cur.execute(query,SCHOOL_CITY=data['school_city'])
        result=qabool_cur.fetchone()
        if result is not None :
            SCHOOL_CITY =result[0]
        else:
            SCHOOL_CITY = None
        '''
        sql = '''INSERT INTO MCSTTEST.SIS_APPLICATIONS ( \
                                          PROCESS_ID, \
                                          SEMESTER,\
                                          NATIONAL_ID,\
                                          FIRST_NAME,\
                                          MID_NAME,\
                                          LAST_NAME,\
                                          FIRST_NAME_S,\
                                          MID_NAME_S,\
                                          LAST_NAME_S, \
                                          STUDY_CODE, \
                                          SCHOOL_COUNTRY, \
                                          SCHOOL_AVG, \
                                          STATUS, \
                                          ENTRY_USER, \
                                          ENTRY_DATE, \
                                          GENDER, \
                                          IS_BRIDGING ,\
                                          IS_EMPLOYEE, \
                                          SCHOOL_YEAR, \
                                          UNIVERSITY_COUNTRY, \
                                          UNIVERSITY_YEAR, \
                                          UNIVERSITY_GPA, \
                                          BIRTH_DATE, \
                                          DEGREE_CODE, \
                                          NATIONALITY_CODE, \
                                          FATHER_NAME, \
                                          FATHER_NAME_S, \
                                          CONSIDERED_NATIONALITY, \
                                          EMAIL, \
                                          PERM_PHONE, \
                                          PERM_COUNTRY, \
                                          PERM_CITY, \
                                          SCHOOL_CODE,\
                                          MAX_UNIVGPA, \
                                          BIRTH_COUNTRY, \
                                          HELTH_STATUS, \
                                          MOBILE_PHONE, \
                                          BIRTH_CITY,\
                                          SCHOOL_ZONE,\
                                          SCHOOL_YEAR_H, \
                                          UNIVERSITY_YEAR_H, \
                                          SCHOOL_CITY, \
                                          PERM_ZIP_CODE, \
                                          TRANSFER_FACULTY, \
                                          TRANSFER_JOINDATE, \
                                          BIRTH_CITY_TEXT, \
                                          LIVING_CITY, \
                                          MOTHER_NATIONALITY,\
                                          REWARD_TYPE,\
                                          MARITAL_STATUS,\
                                          SHEET_NO,\
                                          ADDRESS,\
                                          HOUSE_NO, \
                                          CITY_NAME,\
                                          AREA_NAME) \
                                          VALUES ( \
                                          :PROCESS_ID, \
                                          :SEMESTER,\
                                          :NATIONAL_ID,\
                                          :FIRST_NAME,\
                                          :MID_NAME,\
                                          :LAST_NAME,\
                                          :FIRST_NAME_S,\
                                          :MID_NAME_S,\
                                          :LAST_NAME_S, \
                                          :STUDY_CODE, \
                                          :SCHOOL_COUNTRY, \
                                          :SCHOOL_AVG, \
                                          :STATUS, \
                                          :ENTRY_USER, \
                                          :ENTRY_DATE, \
                                          :GENDER, \
                                          :IS_BRIDGING,\
                                          :IS_EMPLOYEE, \
                                          :SCHOOL_YEAR, \
                                          :UNIVERSITY_COUNTRY, \
                                          :UNIVERSITY_YEAR, \
                                          :UNIVERSITY_GPA, \
                                          :BIRTH_DATE, \
                                          :DEGREE_CODE, \
                                          :NATIONALITY_CODE, \
                                          :FATHER_NAME, \
                                          :FATHER_NAME_S, \
                                          :CONSIDERED_NATIONALITY, \
                                          :EMAIL, \
                                          :PERM_PHONE, \
                                          :PERM_COUNTRY, \
                                          :PERM_CITY ,\
                                          :SCHOOL_CODE,\
                                          :MAX_UNIVGPA, \
                                          :BIRTH_COUNTRY, \
                                          :HELTH_STATUS, \
                                          :MOBILE_PHONE, \
                                          :BIRTH_CITY,\
                                          :SCHOOL_ZONE,\
                                          :SCHOOL_YEAR_H, \
                                          :UNIVERSITY_YEAR_H, \
                                          :SCHOOL_CITY, \
                                          :PERM_ZIP_CODE, \
                                          :TRANSFER_FACULTY, \
                                          :TRANSFER_JOINDATE, \
                                          :BIRTH_CITY_TEXT, \
                                          :LIVING_CITY, \
                                          :MOTHER_NATIONALITY,\
                                          :REWARD_TYPE,\
                                          :MARITAL_STATUS,\
                                          :SHEET_NO,\
                                          :ADDRESS,\
                                          :HOUSE_NO,\
                                          :CITY_NAME,\
                                          :AREA_NAME)'''

        qabool_cur.execute(sql, PROCESS_ID=new_id,
                           SEMESTER=int(data['apply_semester']),
                           NATIONAL_ID=data['national_id'],
                           FIRST_NAME=data['arabic_first_name'],
                           MID_NAME=data['arabic_last_name'],
                           LAST_NAME=data['arabic_family_name'],
                           FIRST_NAME_S=data['first_name'],
                           MID_NAME_S=data['last_name'],
                           LAST_NAME_S=data['family_name'],
                           STUDY_CODE=1,
                           SCHOOL_COUNTRY=data['school_country'],
                           SCHOOL_AVG=data['high_school_GPA'],
                           STATUS=10,
                           ENTRY_USER=407,
                           ENTRY_DATE=data['entry_date'],
                           GENDER=data['gender'],
                           IS_BRIDGING=data['is_pred'],
                           IS_EMPLOYEE=data['employ'],
                           SCHOOL_YEAR=data['high_school_year'],
                           UNIVERSITY_COUNTRY=data['univ_country'],
                           UNIVERSITY_YEAR=data['last_semester'],
                           UNIVERSITY_GPA=data['previous_GPA'],
                           BIRTH_DATE=data['birth_date'],
                           DEGREE_CODE=2,
                           NATIONALITY_CODE=data['country_code'],
                           FATHER_NAME=data['arabic_middle_name'],
                           FATHER_NAME_S=data['middle_name'],
                           CONSIDERED_NATIONALITY=data['considered_nationality'],
                           EMAIL=data['email'],
                           PERM_PHONE=data['home_phone'],
                           PERM_COUNTRY=data['country_code'],
                           PERM_CITY=data['city'],
                           SCHOOL_CODE=data['school_code'],
                           MAX_UNIVGPA=data['max_gpa'],
                           BIRTH_COUNTRY=data['country_code'],
                           HELTH_STATUS=6,
                           MOBILE_PHONE=data['phone'],
                           BIRTH_CITY=data['city'],
                           SCHOOL_ZONE=data['school_zone'],
                           SCHOOL_YEAR_H=data['high_school_year'],
                           UNIVERSITY_YEAR_H=data['high_graduation_year'],
                           SCHOOL_CITY=data['school_city'],
                           PERM_ZIP_CODE=data['postal_code'],
                           TRANSFER_FACULTY=data['previous_university'],
                           TRANSFER_JOINDATE=data['registration_date'],
                           BIRTH_CITY_TEXT=data['birth_place'],
                           LIVING_CITY=data['city'],
                           MOTHER_NATIONALITY=data['mother_country_code'],
                           REWARD_TYPE=0,
                           MARITAL_STATUS=data['marital_status'],
                           SHEET_NO=data['street_no'],
                           ADDRESS=data['address'],
                           HOUSE_NO=data['building_no'],
                           CITY_NAME=data['city_name'],
                           AREA_NAME=data['district']
                           )

        conn.commit()

        sql2 = '''INSERT INTO MCSTTEST.SIS_ADMINEXAM_MARKS(SEMESTER,PROCESS_ID,EXAM_CODE,MARK,ENTRY_USER,ENTRY_DATE)\
                                                   VALUES (:SEMESTER,:PROCESS_ID,:EXAM_CODE,:MARK,:ENTRY_USER,:ENTRY_DATE)'''
        qabool_cur.execute(sql2, SEMESTER=int(data['apply_semester']), PROCESS_ID=new_id, EXAM_CODE=1,
                           MARK=data['qudrat'], ENTRY_USER=407, ENTRY_DATE=data['entry_date'])
        conn.commit()

        qabool_cur.execute(sql2, SEMESTER=int(data['apply_semester']), PROCESS_ID=new_id, EXAM_CODE=2,
                           MARK=data['tahsily'], ENTRY_USER=407, ENTRY_DATE=data['entry_date'])
        conn.commit()

        sql3 = 'INSERT INTO MCSTTEST.SIS_APPLICATION_REFERENCES (NAME,\
                                                        SEMESTER,\
                                                        PROCESS_ID,\
                                                        MOBILE_NO,\
                                                        RELATIONSHIP_CODE,\
                                                        ENTRY_USER,\
                                                        ENTRY_DATE,\
                                                        NATIONAL_ID) \
                                                        VALUES(\
                                                        :NAME,\
                                                        :SEMESTER,\
                                                        :PROCESS_ID,\
                                                        :MOBILE_NO,\
                                                        :RELATIONSHIP_CODE,\
                                                        :ENTRY_USER,\
                                                        :ENTRY_DATE,\
                                                        :NATIONAL_ID) \
                '
        qabool_cur.execute(sql3, NAME=data['ref_name'],
                           SEMESTER=data['apply_semester'],
                           PROCESS_ID=new_id,
                           MOBILE_NO=data['ref_phone'],
                           RELATIONSHIP_CODE=11,
                           ENTRY_USER=407,
                           ENTRY_DATE=data['entry_date'],
                           NATIONAL_ID=data['ref_national_id']
                           )
        conn.commit()
        conn.close()

    else:
        raise Exception("Conncetion Error")


def insert_major(data):
    conn = cx_Oracle.connect("QABOOL_USER/QABOOL_USER@10.101.1.11:1521/ORCL", encoding="utf-8")
    qabool_cur = conn.cursor()

    query = 'select process_id from mcsttest.sis_applications where SEMESTER = :semester and NATIONAL_ID=:national_id'
    qabool_cur.execute(query, semester=int(data['apply_semester']), national_id=data['national_id'])
    result = qabool_cur.fetchone()
    if result is None:
        p_id = 1
    else:
        p_id = result[0]

    if qabool_cur:
        sql = 'INSERT INTO MCSTTEST.SIS_APPLICATION_CHOICES (PROCESS_ID,\
                                                    SEMESTER,\
                                                    CHOICE,\
                                                    IS_ASSIGNED,\
                                                    OPTION_SEQ,\
                                                    CAMPUS_NO,\
                                                    STATUS_CODE,\
                                                    ENTRY_USER,\
                                                    ENTRY_DATE,\
                                                    CHOICE_SEMESTER, \
                                                    APPROVAL_STATUS, \
                                                    IS_WITHDRAWN, \
                                                    IS_TRANSFER_CHOICE ) \
                                                    VALUES(\
                                                    :PROCESS_ID,\
                                                    :SEMESTER,\
                                                    :CHOICE,\
                                                    :IS_ASSIGNED,\
                                                    :OPTION_SEQ,\
                                                    :CAMPUS_NO,\
                                                    :STATUS_CODE,\
                                                    :ENTRY_USER,\
                                                    :ENTRY_DATE,\
                                                    :CHOICE_SEMESTER, \
                                                    :APPROVAL_STATUS, \
                                                    :IS_WITHDRAWN, \
                                                    :IS_TRANSFER_CHOICE ) \
            '
        qabool_cur.execute(sql, PROCESS_ID=p_id,
                           SEMESTER=int(data['apply_semester']),
                           CHOICE=data['major'],
                           IS_ASSIGNED=0,
                           OPTION_SEQ=1,  # hint
                           CAMPUS_NO=1,
                           STATUS_CODE=6,
                           ENTRY_USER=407,
                           ENTRY_DATE=data['entry_date'],
                           CHOICE_SEMESTER=int(data['apply_semester']),
                           APPROVAL_STATUS=data['approval_status'],
                           IS_WITHDRAWN=0,
                           IS_TRANSFER_CHOICE=0)
        conn.commit()
        conn.close()

    else:
        raise Exception("Conncetion Error")
