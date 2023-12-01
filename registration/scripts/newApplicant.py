import logging

from django.conf import settings
from django.utils.timezone import now

from registration.models.applicant import Applicant, STATE_UNIVERSITY_CHOICES
from .oracle import Oracle

logger_oracle = logging.getLogger('oracle_logs')
logger = logging.getLogger('oracle_logs')


class NewApplicant:
    """
        this class is get the new applicant to inserted in E-register
        It takes only one parameter which is object of type Applicant Model
    """

    __DB_VIEW = settings.ORACLE

    def __init__(self, applicant):
        if not isinstance(applicant, Applicant):
            raise Exception("this object isn't instance from applicant model")

        self._applicant = applicant
        self._oracle = Oracle()
        self.__Schema = settings.ORACLE

    def _get_new_process_id(self):
        query = f'select max(process_id) from {self.__DB_VIEW}.sis_applications ' \
                f'where SEMESTER = :semester group by ("SEMESTER")'

        # execute select query
        process = self._oracle.select(query, fetch="one", semester=self._applicant.apply_semester)

        if not isinstance(process, Exception):
            # check and add new process id
            if process is None:
                return 1
            else:
                return process[0] + 1
        message = f"[NEW-APPLICANT-LAST-PROCESS-ID] can't get the applicant id from E-register " \
                  f"with national id {self._applicant.national_id} and failure is {process}"
        logger_oracle.exception(message)
        return process

    def _get_applicant_process_id(self):
        query = f'select process_id from {self.__DB_VIEW}.sis_applications where SEMESTER=:semester and ' \
                f'national_id=:national_id order by process_id desc'

        # execute select query
        process = self._oracle.select(query, fetch="one", semester=self._applicant.apply_semester,
                                      national_id=self._applicant.national_id)
        if process:
            return process[0]

        message = f"[NEW-APPLICANT-PROCESS-ID] can't get the applicant id from E-register " \
                  f"with national id {self._applicant.national_id} and failure is {process}"
        logger_oracle.exception(message)
        return False

    def _prepare_data(self):
        entry_date = now().strftime("%d-%b-%Y")
        process_id = self._get_new_process_id()

        if isinstance(process_id, Exception):
            return process_id

        if self._applicant.building_no and self._applicant.street_no and self._applicant.district \
                and self._applicant.city and self._applicant.nationality:
            address = self._applicant.building_no + ' ' + self._applicant.street_no + ' ' + self._applicant.district \
                      + ' ' + self._applicant.city + ' ' + self._applicant.nationality
        else:
            address = None
        sis_app_data = {

            "PROCESS_ID": process_id,

            # applicant info data

            # arabic name
            "FIRST_NAME": self._applicant.arabic_first_name,
            "FATHER_NAME": self._applicant.arabic_middle_name,
            "MID_NAME": self._applicant.arabic_last_name,
            "LAST_NAME": self._applicant.arabic_family_name,

            # english name
            "FIRST_NAME_S": self._applicant.first_name,
            "FATHER_NAME_S": self._applicant.middle_name,
            "MID_NAME_S": self._applicant.last_name,
            "LAST_NAME_S": self._applicant.family_name,

            # info applicant
            "MARITAL_STATUS": self._applicant.marital_status,
            "GENDER": 1 if self._applicant.gender == "M" else 2,
            "NATIONAL_ID": self._applicant.national_id,
            "EMAIL": self._applicant.email,
            "MOBILE_PHONE": self._applicant.phone,
            "PERM_PHONE": self._applicant.home_phone,
            "BIRTH_DATE": self._applicant.birth_date.strftime("%d-%b-%Y"),
            "BIRTH_COUNTRY": None,
            "NATIONALITY_CODE": None,
            "PERM_COUNTRY": None,
            "CONSIDERED_NATIONALITY": None,
            "MOTHER_NATIONALITY": None,

            # address info
            "STREET_NAME": self._applicant.street_no,
            'HOUSE_NO': self._applicant.building_no,
            'CITY_NAME': self._applicant.city,
            'AREA_NAME': self._applicant.district,
            "ADDRESS": address,
            "PERM_BOBOX": self._applicant.postal_code,
            "PERM_CITY": None,
            "BIRTH_CITY": None,
            "LIVING_CITY": None,

            # school info
            "SCHOOL_AVG": self._applicant.high_school_GPA,
            "SCHOOL_YEAR": self._applicant.high_school_year,
            "SCHOOL_YEAR_H": self._applicant.high_school_year,
            "IS_BRIDGING": 1 if self._applicant.tagseer_GPA is not None else 0,
            "SCHOOL_BRANCH": 1 if self._applicant.secondary_type == 'علمي' else 4,
            "SCHOOL_CODE": None,
            "SCHOOL_CITY": None,
            "SCHOOL_COUNTRY": None,
            "SCHOOL_ZONE": None,

            # tagseer info
            "PREV_MAJOR": self._applicant.tagseer_department,
            "UNIVERSITY_GPA": self._applicant.tagseer_GPA,
            "UNIVERSITY_YEAR_H": self._applicant.tagseer_year if self._applicant.tagseer_year else None,
            "UNIVERSITY_COUNTRY": None,

            # previous university info
            "TRANSFER_FACULTY": self._applicant.previous_university,
            "TRANSFER_GPA": self._applicant.previous_GPA,
            "MAX_TRANSGPA": self._applicant.max_gpa,
            "UNIVERSITY_YEAR": self._applicant.last_semester,
            "TRANSFER_STATUS": dict(STATE_UNIVERSITY_CHOICES)[
                self._applicant.state_university] if self._applicant.state_university else None,
            "IS_TRANSFERED": 1 if self._applicant.previous_GPA is not None else 0,
            "PREV_UNIVERSITY": None,

            # other info
            "SEMESTER": int(self._applicant.apply_semester),
            "TRANSFER_JOINDATE": self._applicant.registration_date.strftime("%d-%b-%Y"),
            "STUDY_CODE": 1,
            "STATUS": 10,
            "ENTRY_DATE": entry_date,
            "ENTRY_USER": 407,
            "DEGREE_CODE": 2,
            "HELTH_STATUS": 6,
            "REWARD_TYPE": 0,
            "TUITION_NO": 10,
        }
        sis_admin_exam_qudrate_data = {
            "PROCESS_ID": process_id,
            "SEMESTER": self._applicant.apply_semester,
            "EXAM_CODE": 1,
            "MARK": self._applicant.qiyas_aptitude,
            "ENTRY_USER": 407,
            "ENTRY_DATE": entry_date,
        }
        sis_admin_exam_tahsily_data = {
            "PROCESS_ID": process_id,
            "SEMESTER": self._applicant.apply_semester,
            "EXAM_CODE": 2,
            "MARK": self._applicant.qiyas_achievement,
            "ENTRY_USER": 407,
            "ENTRY_DATE": entry_date,
        }
        sis_application_reference_data = {
            "PROCESS_ID": process_id,
            "SEMESTER": self._applicant.apply_semester,
            "MOBILE_NO": self._applicant.superior_phone,
            "RELATIONSHIP_CODE": self._applicant.superior_relation,
            "ENTRY_USER": 407,
            "ENTRY_DATE": entry_date,
            "NATIONAL_ID": self._applicant.superior_nationalID,
            "NAME": self._applicant.superior_name
        }

        # employee info
        if self._applicant.employment_state == 'work':
            if self._applicant.employer == 1:
                sis_app_data["IS_EMPLOYEE"] = 2

            elif self._applicant.employer == 2:
                sis_app_data["IS_EMPLOYEE"] = 1

            else:
                sis_app_data["IS_EMPLOYEE"] = 0

        else:
            sis_app_data["IS_EMPLOYEE"] = 0

        if self._applicant.high_school_name:
            # get data from school
            query = f"SELECT SCHOOL_NO, COUNTRY_NO, CITY_NO from {self.__Schema}.SIS_SCHOOLS " \
                    f"WHERE SCHOOL_NAME='{self._applicant.high_school_name}' " \
                    f"OR SCHOOL_NAME_S= '{self._applicant.high_school_name}'"
            schools_data = self._oracle.select(query, fetch='one')

            logger.exception(f"[APPLICANT][HIGH SCHOOL `NAME` ORACLE DATA] - {schools_data}")

            if schools_data:
                try:
                    sis_app_data['SCHOOL_CODE'] = schools_data[0]
                    sis_app_data['SCHOOL_CITY'] = schools_data[2]
                    query = f"SELECT ZONE_CODE from {self.__Schema}.GEN_CITIES WHERE CITY_NO='{schools_data[2]}'"
                    zone = self._oracle.select(query, fetch='one')
                    logger.exception(f"[APPLICANT][HIGH SCHOOL `ZONE` ORACLE DATA] - {zone}")

                    if zone:
                        combination_query = f"SELECT COUNTRY_NO,ZONE_CODE from {self.__Schema}.GEN_COUNTRY_ZONES " \
                                            f"WHERE COUNTRY_NO='{schools_data[1]}' AND ZONE_CODE='{zone[0]}' "

                        country_zone = self._oracle.select(combination_query, fetch='one')
                        logger.exception(f"[APPLICANT][GEN_COUNTRY_ZONES ORACLE DATA] - {country_zone}")
                        if country_zone:
                            sis_app_data['SCHOOL_COUNTRY'] = country_zone[0]
                            sis_app_data['SCHOOL_ZONE'] = country_zone[1]
                        else:
                            # Hard-coding SCHOOL COUNTRY and SCHOOL ZONE if that is Not Present in Oracle DB
                            logger.exception(f"[HARDCODE][APPLICANT - {self._applicant.application_no} NATIONAL ID - "
                                             f"{self._applicant.national_id}] [SCHOOL COUNTRY][SCHOOL ZONE]")
                            sis_app_data['SCHOOL_COUNTRY'] = -1
                            sis_app_data['SCHOOL_ZONE'] = 1

                except Exception as e:
                    logger_oracle.exception(f"[ADD][SCHOOL DATA][EXCEPTION] - {e}")

        if self._applicant.nationality:

            # get applicant nationality
            query = f"SELECT COUNTRY_NO from {self.__Schema}.GEN_COUNTRIES WHERE " \
                    f"NATIONALITY='{self._applicant.nationality}' OR NATIONALITY_S='{self._applicant.nationality}'"
            nationality = self._oracle.select(query, fetch='one')

            if nationality:
                sis_app_data['NATIONALITY_CODE'] = nationality[0]
                sis_app_data['PERM_COUNTRY'] = nationality[0]
            else:
                # Hard-coding Nationality and Permanent Country if that is Not Present in Oracle DB
                logger.exception(f"[HARDCODE][APPLICANT - {self._applicant.application_no} NATIONAL ID - "
                                 f"{self._applicant.national_id}] [NATIONALITY CODE][PERMANENT COUNTRY]")
                sis_app_data['NATIONALITY_CODE'] = -1
                sis_app_data['PERM_COUNTRY'] = -1

        if self._applicant.birth_place:
            # get birth country
            query = f"SELECT COUNTRY_NO from {self.__Schema}.GEN_COUNTRIES " \
                    f"WHERE NATIONALITY='{self._applicant.birth_place}' " \
                    f"OR NATIONALITY_S='{self._applicant.birth_place}'"
            birth_country = self._oracle.select(query, fetch='one')

            if birth_country:
                sis_app_data['BIRTH_COUNTRY'] = birth_country[0]

        if self._applicant.mother_nationality:
            # get mother nationality
            query = f"SELECT COUNTRY_NO from {self.__Schema}.GEN_COUNTRIES " \
                    f"WHERE NATIONALITY='{self._applicant.mother_nationality}' " \
                    f"OR NATIONALITY_S='{self._applicant.mother_nationality}'"
            mother_nationality = self._oracle.select(query, fetch='one')

            if mother_nationality:
                sis_app_data['CONSIDERED_NATIONALITY'] = mother_nationality[0]
                sis_app_data['MOTHER_NATIONALITY'] = mother_nationality[0]

        if self._applicant.tagseer_institute:
            # get tagseer university
            query = f"SELECT UNIVERSITY_CODE from {self.__Schema}.SIS_UNIVERSITIES " \
                    f"WHERE UNIVERSITY_DESC='{self._applicant.tagseer_institute}' " \
                    f"OR UNIVERSITY_DESC_S='{self._applicant.tagseer_institute}'"
            tagseer_univ = self._oracle.select(query, fetch='one')

            if tagseer_univ:
                sis_app_data["PREV_UNIVERSITY"] = tagseer_univ[0]

        if self._applicant.tagseer_country:
            # get tagseer country
            query = f"SELECT COUNTRY_CODE from {self.__Schema}.SIS_UNIVERSITIES " \
                    f"WHERE UNIVERSITY_DESC='{self._applicant.tagseer_institute}' " \
                    f"OR UNIVERSITY_DESC_S='{self._applicant.tagseer_institute}'"
            tagseer_country = self._oracle.select(query, fetch='one')

            if tagseer_country:
                sis_app_data['UNIVERSITY_COUNTRY'] = tagseer_country[0]

        message = f"[NEW-APPLICANT-PREPARE-ADD-DATA] The applicant " \
                  f"with national id {self._applicant.national_id}and sis_app_data is {sis_app_data} " \
                  f"and sis_admin_exam_qudarate is {sis_admin_exam_qudrate_data} " \
                  f"and sis_admin_exam_tahsily is {sis_admin_exam_tahsily_data} " \
                  f"and sis_applicant_reference_data is {sis_application_reference_data}"

        logger.debug(message)

        return {
            "sis_app_data": sis_app_data,
            "sis_admin_exam_qudrate_data": sis_admin_exam_qudrate_data,
            "sis_admin_exam_tahsily_data": sis_admin_exam_tahsily_data,
            "sis_application_reference_data": sis_application_reference_data
        }

    def _prepare_update_data(self):
        process_id = self._get_applicant_process_id()
        if isinstance(process_id, bool):
            return False

        if self._applicant.building_no and self._applicant.street_no and self._applicant.district and \
                self._applicant.city and self._applicant.nationality:
            address = self._applicant.building_no + ' ' + self._applicant.street_no + ' ' + self._applicant.district \
                      + ' ' + self._applicant.city + ' ' + self._applicant.nationality
        else:
            address = None
        sis_app_data = {

            # applicant info data
            "PROCESS_ID": process_id,

            # arabic name
            "FIRST_NAME": self._applicant.arabic_first_name,
            "FATHER_NAME": self._applicant.arabic_middle_name,
            "MID_NAME": self._applicant.arabic_last_name,
            "LAST_NAME": self._applicant.arabic_family_name,

            # english name
            "FIRST_NAME_S": self._applicant.first_name,
            "FATHER_NAME_S": self._applicant.middle_name,
            "MID_NAME_S": self._applicant.last_name,
            "LAST_NAME_S": self._applicant.family_name,

            # info applicant
            "MARITAL_STATUS": self._applicant.marital_status,
            "GENDER": 1 if self._applicant.gender == "M" else 2,
            "NATIONAL_ID": self._applicant.national_id,
            "EMAIL": self._applicant.email,
            "MOBILE_PHONE": self._applicant.phone,
            "PERM_PHONE": self._applicant.home_phone,
            "BIRTH_DATE": self._applicant.birth_date.strftime("%d-%b-%Y"),
            "NATIONALITY_CODE": None,
            "PERM_COUNTRY": None,
            "BIRTH_COUNTRY": None,
            "CONSIDERED_NATIONALITY": None,
            "MOTHER_NATIONALITY": None,

            # address info
            "STREET_NAME": self._applicant.street_no,
            'HOUSE_NO': self._applicant.building_no,
            'CITY_NAME': self._applicant.city,
            'AREA_NAME': self._applicant.district,
            "ADDRESS": address,
            "PERM_BOBOX": self._applicant.postal_code,
            "PERM_CITY": None,
            "BIRTH_CITY": None,
            "LIVING_CITY": None,

            # school info
            "SCHOOL_AVG": self._applicant.high_school_GPA,
            "SCHOOL_YEAR": self._applicant.high_school_year,
            "SCHOOL_YEAR_H": self._applicant.high_school_year,
            "IS_BRIDGING": 1 if self._applicant.tagseer_GPA is not None else 0,
            "SCHOOL_BRANCH": 1 if self._applicant.secondary_type == 'علمي' else 4,
            "SCHOOL_ZONE": None,
            "SCHOOL_CODE": None,
            "SCHOOL_CITY": None,
            "SCHOOL_COUNTRY": None,

            # tagseer info
            "PREV_UNIVERSITY": self._applicant.tagseer_institute,
            "PREV_MAJOR": self._applicant.tagseer_department,
            "UNIVERSITY_GPA": self._applicant.tagseer_GPA,
            "UNIVERSITY_YEAR_H": int(self._applicant.tagseer_year) if self._applicant.tagseer_year else None,
            "UNIVERSITY_COUNTRY": None,

            # previous university info
            "TRANSFER_FACULTY": self._applicant.previous_university,
            "TRANSFER_GPA": self._applicant.previous_GPA,
            "MAX_TRANSGPA": self._applicant.max_gpa,
            "UNIVERSITY_YEAR": self._applicant.last_semester,
            "TRANSFER_STATUS": dict(STATE_UNIVERSITY_CHOICES)[
                self._applicant.state_university] if self._applicant.state_university else None,
            "IS_TRANSFERED": 1 if self._applicant.previous_GPA is not None else 0,

            # other info
            "SEMESTER": int(self._applicant.apply_semester),
            "TRANSFER_JOINDATE": self._applicant.registration_date.strftime("%d-%b-%Y"),  # 49
        }
        sis_application_reference_data = {
            "PROCESS_ID": process_id,
            "SEMESTER": self._applicant.apply_semester,
            "MOBILE_NO": self._applicant.superior_phone,
            "RELATIONSHIP_CODE": self._applicant.superior_relation,
            "NATIONAL_ID": self._applicant.superior_nationalID,
            "NAME": self._applicant.superior_name
        }

        # employee info
        if self._applicant.employment_state == 'work':
            if self._applicant.employer == 1:
                sis_app_data["IS_EMPLOYEE"] = 2

            elif self._applicant.employer == 2:
                sis_app_data["IS_EMPLOYEE"] = 1
        else:
            sis_app_data["IS_EMPLOYEE"] = 0

        if self._applicant.high_school_name:
            # get data from school
            query = f"SELECT SCHOOL_NO, COUNTRY_NO, CITY_NO from {self.__Schema}.SIS_SCHOOLS " \
                    f"WHERE SCHOOL_NAME='{self._applicant.high_school_name}' " \
                    f"OR SCHOOL_NAME_S= '{self._applicant.high_school_name}'"
            schools_data = self._oracle.select(query, fetch='one')

            logger.exception(f"[APPLICANT][HIGH SCHOOL `NAME` ORACLE DATA] - {schools_data}")

            if schools_data:
                try:
                    sis_app_data['SCHOOL_CODE'] = schools_data[0]
                    sis_app_data['SCHOOL_CITY'] = schools_data[2]
                    query = f"SELECT ZONE_CODE from {self.__Schema}.GEN_CITIES WHERE CITY_NO='{schools_data[2]}'"
                    zone = self._oracle.select(query, fetch='one')
                    logger.exception(f"[APPLICANT][HIGH SCHOOL `ZONE` ORACLE DATA] - {zone}")

                    if zone:
                        combination_query = f"SELECT COUNTRY_NO,ZONE_CODE " \
                                            f"from {self.__Schema}.GEN_COUNTRY_ZONES " \
                                            f"WHERE COUNTRY_NO='{schools_data[1]}' AND ZONE_CODE='{zone[0]}'"

                        country_zone = self._oracle.select(combination_query, fetch='one')
                        logger.exception(f"[APPLICANT][GEN_COUNTRY_ZONES ORACLE DATA] - {country_zone}")
                        if country_zone:
                            sis_app_data['SCHOOL_COUNTRY'] = country_zone[0]
                            sis_app_data['SCHOOL_ZONE'] = country_zone[1]
                        else:
                            # Hard-coding SCHOOL COUNTRY and SCHOOL ZONE if that is Not Present in Oracle DB
                            logger.exception(f"[HARDCODE][APPLICANT - {self._applicant.application_no} NATIONAL ID - "
                                             f"{self._applicant.national_id}] [SCHOOL COUNTRY][SCHOOL ZONE]")
                            sis_app_data['SCHOOL_COUNTRY'] = -1
                            sis_app_data['SCHOOL_ZONE'] = 1
                except Exception as e:
                    logger_oracle.exception(f"[UPDATE][SCHOOL DATA][EXCEPTION] - {e}")

        if self._applicant.nationality:

            # get applicant nationality
            query = f"SELECT COUNTRY_NO from {self.__Schema}.GEN_COUNTRIES " \
                    f"WHERE NATIONALITY='{self._applicant.nationality}' " \
                    f"OR NATIONALITY_S='{self._applicant.nationality}'"
            nationality = self._oracle.select(query, fetch='one')

            if nationality:
                sis_app_data['NATIONALITY_CODE'] = nationality[0]
                sis_app_data['PERM_COUNTRY'] = nationality[0]
            else:
                # Hard-coding NATIONALITY CODE and Permanent Country if that is Not Present in Oracle DB
                logger.exception(f"[HARDCODE][APPLICANT - {self._applicant.application_no} NATIONAL ID - "
                                 f"{self._applicant.national_id}] [NATIONALITY CODE][PERMANENT COUNTRY]")
                sis_app_data['NATIONALITY_CODE'] = -1
                sis_app_data['PERM_COUNTRY'] = -1

        if self._applicant.birth_place:
            # get birth country
            query = f"SELECT COUNTRY_NO from {self.__Schema}.GEN_COUNTRIES " \
                    f"WHERE NATIONALITY='{self._applicant.birth_place}' " \
                    f"OR NATIONALITY_S='{self._applicant.birth_place}'"
            birth_country = self._oracle.select(query, fetch='one')

            if birth_country:
                sis_app_data['BIRTH_COUNTRY'] = birth_country[0]

        if self._applicant.mother_nationality:
            # get mother nationality
            query = f"SELECT COUNTRY_NO from {self.__Schema}.GEN_COUNTRIES " \
                    f"WHERE NATIONALITY='{self._applicant.mother_nationality}' " \
                    f"OR NATIONALITY_S='{self._applicant.mother_nationality}'"
            mother_nationality = self._oracle.select(query, fetch='one')

            if mother_nationality:
                sis_app_data['CONSIDERED_NATIONALITY'] = mother_nationality[0]
                sis_app_data['MOTHER_NATIONALITY'] = mother_nationality[0]

        if self._applicant.tagseer_institute:
            # get tagseer university
            query = f"SELECT UNIVERSITY_CODE from {self.__Schema}.SIS_UNIVERSITIES " \
                    f"WHERE UNIVERSITY_DESC='{self._applicant.tagseer_institute}' " \
                    f"OR UNIVERSITY_DESC_S='{self._applicant.tagseer_institute}'"
            tagseer_univ = self._oracle.select(query, fetch='one')

            if tagseer_univ:
                sis_app_data["PREV_UNIVERSITY"] = tagseer_univ[0]

        if self._applicant.tagseer_country:
            # get tagseer country
            query = f"SELECT COUNTRY_CODE from {self.__Schema}.SIS_UNIVERSITIES " \
                    f"WHERE UNIVERSITY_DESC='{self._applicant.tagseer_institute}' " \
                    f"OR UNIVERSITY_DESC_S='{self._applicant.tagseer_institute}'"
            tagseer_country = self._oracle.select(query, fetch='one')

            if tagseer_country:
                sis_app_data['UNIVERSITY_COUNTRY'] = tagseer_country[0]

        message = f"[UPDATE-APPLICANT-PREPARE-DATA] The applicant " \
                  f"with national id {self._applicant.national_id} and sis_app_data is {sis_app_data} " \
                  f"and sis_applicant_reference_data is {sis_application_reference_data}"
        logger.debug(message)
        return {
            "sis_app_data": sis_app_data,
            "sis_application_reference_data": sis_application_reference_data
        }

    def new(self):

        data = self._prepare_data()
        if not isinstance(data, dict):
            return data

        query_param1 = data['sis_app_data']
        query_param2 = data['sis_admin_exam_qudrate_data']
        query_param3 = data['sis_admin_exam_tahsily_data']
        query_param4 = data['sis_application_reference_data']

        query1 = f'''INSERT INTO {self.__DB_VIEW}.SIS_APPLICATIONS ( PROCESS_ID, FIRST_NAME, FATHER_NAME, MID_NAME, 
        LAST_NAME, FIRST_NAME_S, FATHER_NAME_S, MID_NAME_S, LAST_NAME_S, NATIONAL_ID, STATUS, EMAIL, MOBILE_PHONE,
        MARITAL_STATUS, BIRTH_DATE, BIRTH_COUNTRY, REWARD_TYPE, NATIONALITY_CODE, GENDER, HELTH_STATUS, STREET_NAME,
        ADDRESS, HOUSE_NO, CITY_NAME, AREA_NAME, CONSIDERED_NATIONALITY, PERM_PHONE,PERM_COUNTRY, PERM_BOBOX, 
        MOTHER_NATIONALITY, SEMESTER, STUDY_CODE, SCHOOL_COUNTRY, SCHOOL_AVG, SCHOOL_YEAR, SCHOOL_CODE, SCHOOL_ZONE,
        SCHOOL_YEAR_H, IS_BRIDGING, TRANSFER_GPA, DEGREE_CODE, MAX_TRANSGPA, TRANSFER_FACULTY, TRANSFER_JOINDATE,
        UNIVERSITY_YEAR, IS_EMPLOYEE, ENTRY_USER, ENTRY_DATE, IS_TRANSFERED, TRANSFER_STATUS, PREV_UNIVERSITY,
        UNIVERSITY_GPA, PREV_MAJOR, UNIVERSITY_YEAR_H, UNIVERSITY_COUNTRY, SCHOOL_BRANCH, SCHOOL_CITY,PERM_CITY, 
        BIRTH_CITY, LIVING_CITY, TUITION_NO) 
        VALUES (:PROCESS_ID, :FIRST_NAME, :FATHER_NAME, :MID_NAME, :LAST_NAME, :FIRST_NAME_S, :FATHER_NAME_S, 
        :MID_NAME_S, :LAST_NAME_S, :NATIONAL_ID, :STATUS, :EMAIL, :MOBILE_PHONE, :MARITAL_STATUS, :BIRTH_DATE, 
        :BIRTH_COUNTRY, :REWARD_TYPE, :NATIONALITY_CODE, :GENDER, :HELTH_STATUS, :STREET_NAME, :ADDRESS, :HOUSE_NO, 
        :CITY_NAME, :AREA_NAME, :CONSIDERED_NATIONALITY, :PERM_PHONE, :PERM_COUNTRY, :PERM_BOBOX, :MOTHER_NATIONALITY, 
        :SEMESTER, :STUDY_CODE, :SCHOOL_COUNTRY, :SCHOOL_AVG, :SCHOOL_YEAR, :SCHOOL_CODE, :SCHOOL_ZONE, :SCHOOL_YEAR_H,
        :IS_BRIDGING, :TRANSFER_GPA, :DEGREE_CODE, :MAX_TRANSGPA, :TRANSFER_FACULTY, :TRANSFER_JOINDATE,
        :UNIVERSITY_YEAR, :IS_EMPLOYEE, :ENTRY_USER, :ENTRY_DATE, :IS_TRANSFERED, :TRANSFER_STATUS,
        :PREV_UNIVERSITY, :UNIVERSITY_GPA, :PREV_MAJOR, :UNIVERSITY_YEAR_H, :UNIVERSITY_COUNTRY,
        :SCHOOL_BRANCH, :SCHOOL_CITY, :PERM_CITY, :BIRTH_CITY, :LIVING_CITY, :TUITION_NO)'''

        query2 = f'''INSERT INTO {self.__DB_VIEW}.SIS_ADMINEXAM_MARKS(SEMESTER,PROCESS_ID,EXAM_CODE,MARK,ENTRY_USER,
        ENTRY_DATE) VALUES (:SEMESTER,:PROCESS_ID,:EXAM_CODE,:MARK,:ENTRY_USER,:ENTRY_DATE)'''

        query3 = f'''INSERT INTO {self.__DB_VIEW}.SIS_APPLICATION_REFERENCES (NAME, SEMESTER, PROCESS_ID, MOBILE_NO,
        RELATIONSHIP_CODE, ENTRY_USER, ENTRY_DATE, NATIONAL_ID) 
        VALUES(:NAME, :SEMESTER, :PROCESS_ID, :MOBILE_NO, :RELATIONSHIP_CODE, :ENTRY_USER, :ENTRY_DATE, :NATIONAL_ID)'''

        # insert into SIS_APPLICATION
        insert_q1 = self._oracle.insert(query1, **query_param1)
        if isinstance(insert_q1, bool):
            message = f"[NEW-APPLICANT-INSERT] success added `sis_applicant` The applicant with national id " \
                      f"{self._applicant.national_id} and data is {query_param1}"
            logger.debug(message)

            # insert into SIS_ADMIN EXAM_MARKS with exam qiyas aptitude
            insert_q2 = self._oracle.insert(query2, **query_param2)
            if isinstance(insert_q2, bool):
                message = f"[NEW-APPLICANT-INSERT] success added `exam qiyas aptitude` The applicant with national id " \
                          f"{self._applicant.national_id} and data is {query_param2}"

                logger.debug(message)

                # insert into SIS_ADMIN EXAM_MARKS with exam qiyas achievement
                insert_q3 = self._oracle.insert(query2, **query_param3)
                if isinstance(insert_q3, bool):
                    message = f"[NEW-APPLICANT-INSERT] success added `exam qiyas achievement` The applicant with " \
                              f"national id {self._applicant.national_id} and data is {query_param3}"
                    logger.debug(message)

                    # insert into SIS_APPLICATION_REFERENCES
                    insert_q4 = self._oracle.insert(query3, **query_param4)

                    if isinstance(insert_q4, bool):
                        message = f"[NEW-APPLICANT-INSERT] success added `sis applicant reference` The applicant with" \
                                  f" national id {self._applicant.national_id}  and data is {query_param4}"

                        logger.debug(message)

                        self._oracle.close_connection()
                        return True

                    else:
                        message = f"[NEW-APPLICANT-INSERT] fail added `sis applicant reference` The applicant " \
                                  f"with national id {self._applicant.national_id} and " \
                                  f"DATA: {query_param4} & QUERY - None FAILURE : {insert_q4}"

                        logger_oracle.exception(message)
                        self._oracle.close_connection()
                        return insert_q4
                else:
                    message = f"[NEW-APPLICANT-INSERT] failed to added `exam qiyas achievement` The applicant " \
                              f"with national id {self._applicant.national_id} and " \
                              f"DATA: {query_param3} & QUERY - {query3} & FAILURE : {insert_q3}"

                    logger_oracle.exception(message)
                    self._oracle.close_connection()
                    return insert_q3
            else:
                message = f"[NEW-APPLICANT-INSERT] failed to added `exam qiyas aptitude` The applicant " \
                          f"with national id {self._applicant.national_id} and " \
                          f"DATA: {query_param2}  & QUERY - {query2}  & FAILURE : {insert_q2}"

                logger_oracle.exception(message)
                self._oracle.close_connection()
                return insert_q2

        message = f"[NEW-APPLICANT-INSERT] failed to added `sis_applicant` The applicant with " \
                  f"national id {self._applicant.national_id} and " \
                  f"DATA: {query_param1} & QUERY - {query1} & FAILURE : {insert_q1}"

        logger_oracle.exception(message)
        self._oracle.close_connection()
        return insert_q1

    def update(self):
        data = self._prepare_update_data()

        if isinstance(data, bool):
            return Exception(
                f"{self._applicant.national_id} this applicant with that national id isn't found in E-register")

        query_param1 = data['sis_app_data']
        query_param2 = data['sis_application_reference_data']

        query1 = f'''update {self.__DB_VIEW}.SIS_APPLICATIONS set FIRST_NAME=:FIRST_NAME, FATHER_NAME=:FATHER_NAME, 
                            MID_NAME=:MID_NAME, LAST_NAME=:LAST_NAME, FIRST_NAME_S=:FIRST_NAME_S, 
                            FATHER_NAME_S=:FATHER_NAME_S, MID_NAME_S=:MID_NAME_S, LAST_NAME_S=:LAST_NAME_S, 
                            NATIONAL_ID=:NATIONAL_ID, EMAIL=:EMAIL, MOBILE_PHONE=:MOBILE_PHONE, 
                            MARITAL_STATUS=:MARITAL_STATUS, BIRTH_DATE=:BIRTH_DATE, BIRTH_COUNTRY=:BIRTH_COUNTRY, 
                            NATIONALITY_CODE=:NATIONALITY_CODE, GENDER=:GENDER, 
                            STREET_NAME=:STREET_NAME, ADDRESS=:ADDRESS, HOUSE_NO=:HOUSE_NO,
                            CITY_NAME=:CITY_NAME, AREA_NAME=:AREA_NAME, CONSIDERED_NATIONALITY=:CONSIDERED_NATIONALITY,
                            PERM_PHONE=:PERM_PHONE, PERM_COUNTRY=:PERM_COUNTRY, PERM_BOBOX=:PERM_BOBOX, 
                            MOTHER_NATIONALITY=:MOTHER_NATIONALITY, SCHOOL_COUNTRY=:SCHOOL_COUNTRY,
                            SCHOOL_AVG=:SCHOOL_AVG, SCHOOL_YEAR=:SCHOOL_YEAR, SCHOOL_CODE=:SCHOOL_CODE,
                            SCHOOL_ZONE=:SCHOOL_ZONE, SCHOOL_YEAR_H=:SCHOOL_YEAR_H, IS_BRIDGING=:IS_BRIDGING,
                            TRANSFER_GPA=:TRANSFER_GPA, MAX_TRANSGPA=:MAX_TRANSGPA, 
                            TRANSFER_FACULTY=:TRANSFER_FACULTY, TRANSFER_JOINDATE=:TRANSFER_JOINDATE,
                            UNIVERSITY_YEAR=:UNIVERSITY_YEAR, IS_EMPLOYEE=:IS_EMPLOYEE, IS_TRANSFERED=:IS_TRANSFERED, 
                            TRANSFER_STATUS=:TRANSFER_STATUS, PREV_UNIVERSITY=:PREV_UNIVERSITY,
                            UNIVERSITY_GPA=:UNIVERSITY_GPA, PREV_MAJOR=:PREV_MAJOR,
                            UNIVERSITY_YEAR_H=:UNIVERSITY_YEAR_H, UNIVERSITY_COUNTRY=:UNIVERSITY_COUNTRY,
                            SCHOOL_BRANCH=:SCHOOL_BRANCH, SCHOOL_CITY=:SCHOOL_CITY, PERM_CITY=:PERM_CITY, 
                            BIRTH_CITY=:BIRTH_CITY, LIVING_CITY=:LIVING_CITY
                            where PROCESS_ID=:PROCESS_ID and SEMESTER=:SEMESTER'''

        query2 = f'''UPDATE {self.__DB_VIEW}.SIS_APPLICATION_REFERENCES SET NAME=:NAME, MOBILE_NO=:MOBILE_NO,
                    RELATIONSHIP_CODE=:RELATIONSHIP_CODE, NATIONAL_ID=:NATIONAL_ID 
                    WHERE SEMESTER=:SEMESTER AND PROCESS_ID=:PROCESS_ID '''

        # update in SIS_APPLICATION
        update = self._oracle.update(query1, **query_param1)
        if not isinstance(update, bool):
            message = f"[NEW-APPLICANT-UPDATE] fail updated `sis_applicant` The applicant " \
                      f"with national id {self._applicant.national_id} and " \
                      f"DATA : {query_param1} & QUERY : {query1} & FAILURE : {update}"

            logger_oracle.exception(message)
            self._oracle.close_connection()
            return update

        message = f"[NEW-APPLICANT-UPDATE] success updated `sis_applicant` The applicant " \
                  f"with national id {self._applicant.national_id} and data is {query_param1}"

        logger.debug(message)

        # update in SIS_APPLICATION_REFERENCES
        update2 = self._oracle.update(query2, **query_param2)

        if not isinstance(update2, bool):
            message = f"[NEW-APPLICANT-UPDATE] fail updated `sis applicant reference` The applicant " \
                      f"with national id {self._applicant.national_id} and " \
                      f"DATA : {query_param2} & QUERY : {query2} & FAILURE : {update2}"
            logger_oracle.exception(message)
            self._oracle.close_connection()
            return update2

        message = f"[NEW-APPLICANT-UPDATE] success updated `sis applicant reference` The applicant " \
                  f"with national id {self._applicant.national_id}  and data is {query_param2}"

        logger.debug(message)

        self._oracle.close_connection()
        return True

    def update_score(self):

        process_id = self._get_applicant_process_id()

        if isinstance(process_id, bool):
            return Exception(
                f"{self._applicant.national_id} this applicant with that national id isn't found in E-register")

        query1 = f'''update {self.__DB_VIEW}.SIS_APPLICATIONS set SCHOOL_AVG=:high_school_GPA, 
        TRANSFER_GPA=:previous_GPA where NATIONAL_ID=:NATIONAL_ID AND SEMESTER=:SEMESTER'''

        query2 = f'''update {self.__DB_VIEW}.SIS_ADMINEXAM_MARKS set MARK=:MARK,LAST_UPDATE_DATE=:last_date 
        where PROCESS_ID=:PROCESS_ID AND SEMESTER=:SEMESTER AND EXAM_CODE=1'''

        query3 = f'''update {self.__DB_VIEW}.SIS_ADMINEXAM_MARKS set MARK=:MARK,LAST_UPDATE_DATE=:last_date 
        where PROCESS_ID=:PROCESS_ID AND SEMESTER=:SEMESTER AND EXAM_CODE=2'''

        data = {
            "high_school_GPA": self._applicant.high_school_GPA,
            "previous_GPA": self._applicant.previous_GPA,
            "NATIONAL_ID": self._applicant.national_id,
            "SEMESTER": self._applicant.apply_semester,
        }
        # update previous gpa and high school gpa
        update = self._oracle.update(query1, **data)

        if not isinstance(update, bool):
            message = f"[NEW-APPLICANT-UPDATE-SCORE] fail updated `previous gpa and high school gpa` The applicant " \
                      f"with national id {self._applicant.national_id} and data is {data} and failure is {update}"

            logger_oracle.exception(message)
            self._oracle.close_connection()
            return update

        message = f"[NEW-APPLICANT-UPDATE-SCORE] success updated `previous gpa and high school gpa` The applicant " \
                  f"with national id {self._applicant.national_id} and data is {data}"

        logger.debug(message)

        data = {
            "MARK": self._applicant.qiyas_aptitude,
            "last_date": now().strftime("%d-%b-%Y"),
            "PROCESS_ID": process_id,
            "SEMESTER": self._applicant.apply_semester,
        }

        # update qudrat exam
        update2 = self._oracle.update(query2, **data)

        if not isinstance(update2, bool):
            message = f"[NEW-APPLICANT-UPDATE-SCORE] fail updated `qudrat exam` The applicant " \
                      f"with national id {self._applicant.national_id} and data is {data} and failure is {update2}"
            logger_oracle.exception(message)
            self._oracle.close_connection()
            return update2

        message = f"[NEW-APPLICANT-UPDATE-SCORE] success updated `qudrat exam` The applicant " \
                  f"with national id {self._applicant.national_id} and data is {data}"
        logger.debug(message)

        data = {
            "MARK": self._applicant.qiyas_achievement,
            "last_date": now().strftime("%d-%b-%Y"),
            "PROCESS_ID": process_id,
            "SEMESTER": self._applicant.apply_semester,
        }

        # update tahsily exam
        update3 = self._oracle.update(query3, **data)

        if not isinstance(update3, bool):
            message = f"[NEW-APPLICANT-UPDATE-SCORE] fail updated `tahsily exam` The applicant " \
                      f"with national id {self._applicant.national_id}  and data is {data} and failure is {update3}"
            logger_oracle.exception(message)
            self._oracle.close_connection()
            return update3

        message = f"[NEW-APPLICANT-UPDATE-SCORE] success updated `tahsily exam` The applicant " \
                  f"with national id {self._applicant.national_id}  and data is {data}"
        logger.debug(message)
        self._oracle.close_connection()
        return True
