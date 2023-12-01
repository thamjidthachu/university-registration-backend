import logging

from django.conf import settings

from registration.models.applicant import Applicant
from .oracle import Oracle

logger = logging.getLogger('oracle_logs')


class Major:
    """
        this class is get the all majors that added to the current applicant to inserted in E-register
        It takes only one parameter which is object of type Applicant Model
    """

    CHOICES = {
        'first_periority': 1, 'second_periority': 2, 'third_periority': 3, 'fourth_periority': 4, 'fifth_periority': 5,
        'sixth_periority': 6, 'seventh_periority': 7, 'eighth_periority': 8, 'ninth_periority': 9, 'tenth_periority': 10
    }

    OPTION_SEQUENCE = {
        # key is concat by major_gender_bridging
        "1_1_0": 21, "1_2_0": 22, "2_2_1": 17, "2_1_1": 14, "2_2_0": 8, "2_1_0": 2, "3_1_0": 3, "3_2_0": 9, "3_1_1": 15,
        "3_2_1": 18, "4_1_0": 4, "4_2_1": 19, "4_2_0": 10, "4_1_1": 16, "5_2_0": 11, "5_1_0": 5, "6_1_0": 6,
        "6_2_0": 12, "7_1_1": 25, "7_2_0": 38, "7_1_0": 20, "8_1_0": 28, "9_1_1": 35, "9_1_0": 31, "9_2_0": 33,
        "9_2_1": 37, "10_1_0": 32, "10_2_0": 34,
    }

    CHOICES_MAJORS = {
        1: 1, 2: 2, 3: 3, 4: 4, 5: 7, 6: 9, 7: 10, 8: 6, 9: 5, 10: 8,
    }

    majors = ['first_periority', 'second_periority', 'third_periority', 'fourth_periority', 'fifth_periority',
              'sixth_periority', 'seventh_periority', 'eighth_periority', 'ninth_periority', 'tenth_periority']

    __DB_VIEW = settings.ORACLE

    def __init__(self, applicant):
        if not isinstance(applicant, Applicant):
            raise Exception("this object isn't instance from applicant model")

        self._applicant = applicant
        self._oracle = Oracle()
        self._process_id = self._get_applicant_process_id()

    def _get_applicant_process_id(self):
        query = f'''
            SELECT PROCESS_ID FROM {self.__DB_VIEW}.SIS_APPLICATIONS WHERE SEMESTER = {self._applicant.apply_semester} 
            AND NATIONAL_ID= {self._applicant.national_id} AND EMAIL= '{self._applicant.email}' ORDER BY PROCESS_ID DESC 
        '''
        process = self._oracle.select(query, fetch="one")

        if process:
            message = f"[MAJOR][PROCESS-ID]- Applicant-ID: `{process[0]}` National-ID: `{self._applicant.national_id}`"
            logger.exception(message)
            return process[0]

        message = f"[MAJOR-PROCESS-ID] couldn't fetch applicant id National-ID - {self._applicant.national_id} and " \
                  f"failure is {process} "
        logger.exception(message)
        return False

    def _prepare_add_major(self):
        logger.exception(f"[B1]")
        prepare_majors = []
        gender = 1 if self._applicant.gender == 'M' else 2
        bridging = 1 if self._applicant.tagseer_department is not None else 0
        logger.exception(f"[B2]: {gender} - {bridging} ")

        for major in self.majors:
            logger.exception(f"[B3]: {major}")
            prior = getattr(self._applicant, major)
            logger.exception(f"[B4][PRIOR] : {prior}")
            if prior in [None, 0, 12]:
                logger.exception(f"[B4.1][PRIOR]")
                continue
            logger.exception(f"[B4.2][PRIOR]")
            periority = self.CHOICES_MAJORS[prior]
            option_seq = f"{periority}_{gender}_{bridging}"
            logger.exception(f"[B5]: {periority} - {option_seq}")

            if option_seq in self.OPTION_SEQUENCE:
                logger.exception(f"[B6]: {option_seq} - {self.OPTION_SEQUENCE}")
                try:
                    prepare_majors.append({
                        "PROCESS_ID": self._process_id,
                        "SEMESTER": int(self._applicant.apply_semester),
                        "CHOICE": self.CHOICES[major],
                        "OPTION_SEQ": self.OPTION_SEQUENCE[option_seq],
                        "CAMPUS_NO": gender,
                        "CHOICE_SEMESTER": int(self._applicant.apply_semester),
                    })
                except Exception as e:
                    logger.exception(f"[B8]: [EXCEPTION][_prepare_add_major] - {e}")
        logger.exception(f"[B7]: {prepare_majors}")
        message = f"[PREPARE-MAJOR-ADD] add majors with national id {self._applicant.national_id} and majors is {prepare_majors} "
        logger.exception(message)
        return prepare_majors

    def _prepare_update_major(self):
        majors = self.select_major()
        num_priorities = sum(getattr(self._applicant, major) is not None for major in self.majors)
        num_majors = len(majors)

        if num_majors == 0:
            return self.add_major()
        elif num_majors == num_priorities:
            return {"update": self._update_fields_majors(majors)}
        elif num_majors > num_priorities:
            num_deleted = num_majors - num_priorities
            self._delete_majors(majors, num_deleted)
            return {"update": self._update_fields_majors(self.select_major())}
        else:
            update_data = self._update_fields_majors(majors)
            gender = 1 if self._applicant.gender == 'M' else 2
            bridging = 1 if self._applicant.tagseer_department is not None else 0
            additional_majors = []

            for value in self.majors[num_majors:]:
                prior = getattr(self._applicant, value)
                periority = self.CHOICES_MAJORS.get(prior)
                if periority is not None:
                    option_seq = f"{periority}_{gender}_{bridging}"
                    if option_seq in self.OPTION_SEQUENCE:
                        additional_majors.append({
                            "PROCESS_ID": self._process_id,
                            "SEMESTER": int(self._applicant.apply_semester),
                            "CHOICE": self.CHOICES[value],
                            "OPTION_SEQ": self.OPTION_SEQUENCE[option_seq],
                            "CAMPUS_NO": gender,
                            "CHOICE_SEMESTER": int(self._applicant.apply_semester),
                        })

            message = f"[PREPARE-MAJOR-UPDATE] update majors with national id {self._applicant.national_id} and " \
                      f"majors added is {additional_majors} and majors updated is {update_data} "
            logger.exception(message)

            return {
                "update": update_data,
                "add": additional_majors
            }

    def _update_fields_majors(self, majors):
        gender = 1 if self._applicant.gender == 'M' else 2
        bridging = 1 if self._applicant.tagseer_department is not None else 0
        updated_majors = []

        for index, major in enumerate(majors):
            prior = getattr(self._applicant, self.majors[index])
            periority = self.CHOICES_MAJORS.get(prior)
            option_seq = f"{periority}_{gender}_{bridging}"

            if periority is not None and major != periority and option_seq in self.OPTION_SEQUENCE:
                updated_majors.append({
                    "PROCESS_ID": self._process_id,
                    "SEMESTER": self._applicant.apply_semester,
                    "CHOICE": self.CHOICES[self.majors[index]],
                    "OPTION_SEQ": self.OPTION_SEQUENCE[option_seq],
                    "OLD_CHOICE": major[0]
                })

        message = f"[MAJOR-UPDATE-FIELDS-MAJORS] update majors with national id {self._applicant.national_id} and " \
                  f"majors updated is {updated_majors} "
        logger.exception(message)

        return updated_majors

    def _delete_majors(self, majors, nums):

        for num in range(nums):
            self._oracle.delete(f'''DELETE FROM {self.__DB_VIEW}.SIS_APPLICATION_CHOICES WHERE CHOICE=:CHOICE AND \
                                   PROCESS_ID=:PROCESS_ID AND SEMESTER=:SEMESTER''', CHOICE=majors[num][0],
                                PROCESS_ID=self._process_id, SEMESTER=self._applicant.apply_semester)

        message = f"[MAJOR-DELETE-FIELDS-MAJORS] delete majors" + \
                  f" with national id {self._applicant.national_id} and " + \
                  f"majors number deleted is {nums} and majors is {majors}"

        logger.exception(message)
        return True

    def add_major(self):
        logger.exception(f"[A1]")
        if isinstance(self._process_id, bool):
            return Exception(
                f"{self._applicant.national_id} this applicant with that national id isn't found in E-register")
        logger.exception(f"[A2][APPLICANT-ID]- {self._process_id}")
        query_param = self._prepare_add_major()
        logger.exception(f"[A3][QUERY-PARAMS]- {query_param}")
        error = False
        query = f'''
            INSERT INTO {self.__DB_VIEW}.SIS_APPLICATION_CHOICES (PROCESS_ID, SEMESTER, CHOICE, OPTION_SEQ, CAMPUS_NO, CHOICE_SEMESTER, ENTRY_DATE)
            VALUES (:PROCESS_ID, :SEMESTER, :CHOICE, :OPTION_SEQ, :CAMPUS_NO, :CHOICE_SEMESTER, sysdate)
        '''

        for param in query_param:
            logger.exception(f"[A4][PARAMS]- {param}")
            insert = self._oracle.insert(query, **param)
            logger.exception(f"[A][INSERT]- Insertion is {insert}")

            if not isinstance(insert, bool):
                error = insert
                message = f"[MAJOR-ADD] add major exception with national id {self._applicant.national_id} and data is {param} and failure is {error}"
                logger.exception(message)
                break

            message = f"[MAJOR-ADD] success add major with national id {self._applicant.national_id} and data is {param}"
            logger.exception(message)

        self._oracle.close_connection()

        if error:
            return error

        return True

    # Update Major
    def update_major(self):

        if isinstance(self._process_id, bool):
            return Exception(
                f"{self._applicant.national_id} this applicant with that national id isn't found in E-register")

        query_param = self._prepare_update_major()
        error = False

        if isinstance(query_param, dict):

            if "update" in query_param:

                query = f'''update {self.__DB_VIEW}.SIS_APPLICATION_CHOICES set CHOICE = :CHOICE, 
                OPTION_SEQ=:OPTION_SEQ WHERE PROCESS_ID=:PROCESS_ID AND SEMESTER=:SEMESTER AND CHOICE=:OLD_CHOICE '''

                for param in query_param['update']:
                    insert = self._oracle.update(query, **param)
                    if not isinstance(insert, bool):
                        error = insert
                        message = f"[MAJOR-UPDATE] update major exception" + \
                                  f" with national id {self._applicant.national_id} and " + \
                                  f"data is {param} and failure is {insert}"

                        logger.exception(message)
                        break
                    message = f"[MAJOR-UPDATE] success updated major" + \
                              f" with national id {self._applicant.national_id} and " + \
                              f"data is {param}"
                    logger.exception(message)

            if 'add' in query_param:
                query = f'''INSERT INTO {self.__DB_VIEW}.SIS_APPLICATION_CHOICES (PROCESS_ID, SEMESTER, CHOICE, 
                OPTION_SEQ,CAMPUS_NO, CHOICE_SEMESTER, ENTRY_DATE) VALUES (:PROCESS_ID, :SEMESTER, :CHOICE, :OPTION_SEQ, 
                :CAMPUS_NO, :CHOICE_SEMESTER, sysdate) '''

                for param in query_param['add']:
                    update = self._oracle.update(query, **param)
                    if not isinstance(update, bool):
                        error = update
                        message = f"[MAJOR-UPDATE] update major exception" + \
                                  f" with national id {self._applicant.national_id} and " + \
                                  f"data is {param} and failure is {update}"

                        logger.exception(message)
                        break

                    message = f"[MAJOR-UPDATE] success update major with national id {self._applicant.national_id} and  self._applicant.apply_semester-data is {param} "

                    logger.exception(message)

            self._oracle.close_connection()

            if error:
                return error

        return True

    def select_major(self):
        query = f'''SELECT CHOICE FROM {self.__DB_VIEW}.SIS_APPLICATION_CHOICES WHERE 
        PROCESS_ID={self._process_id} AND SEMESTER={self._applicant.apply_semester} ORDER BY CHOICE'''
        return self._oracle.select(query)
