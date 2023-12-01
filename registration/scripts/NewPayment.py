import logging
import re

from django.conf import settings
from .oracle import Oracle

logger = logging.getLogger("oracle_payment_updates")


class PaymentPush:
    current_semester = None
    service_number = None
    start_date = None
    applicant_process_id = None
    oracle = None
    errors = {}
    SCHEMA = settings.ORACLE

    def __init__(self):
        logger.debug("[PAYMENT INSERTION STARTED]................")
        self.oracle = Oracle()
        # load the important query
        self.__get_current_semester()
        self.__get_service_number()
        self.__get_start_date()
        self.errors = {}
        self.service_number = None

    def __get_current_semester(self):
        success = False
        try:
            query = f"SELECT SEMESTER FROM {self.SCHEMA}.SIS_DEGREE_CALENDAR WHERE IS_CLOSED=0 and IS_AUTO_CLOSED=0 " \
                    f"and DEGREE_CODE=2 and IS_ACTIVATED = 1 "

            result = self.oracle.select(query, fetch='one')
            if result:
                success = True
            logger.debug(f"[CURRENT-SEMESTER] query status - {success}, result - {result}")

            if not success:
                self.errors['current_semester_query'] = \
                    f"failed to fetch the current semester due to the error {result}, query {query} "
                return

            if result is None:
                self.errors['current_semester_query'] = f"the result is empty"
                return

            self.current_semester = result[0]
            return
        except Exception as e:
            logger.debug(f"[CURRENT-SEMESTER] [EXCEPTION] - {e}")

    def __get_service_number(self):
        success = False
        try:
            query = f"SELECT Max(SERVICE_NO) FROM {self.SCHEMA}.SAS_STUDENT_CLAIMS"

            result = self.oracle.select(query, fetch='one')
            if result:
                success = True
            logger.debug(f"[GET-LAST-SERVICE-NUMBER] query status - {success}, result - {result}")
            if not success:
                self.errors['service_number_query'] = \
                    f"failed to fetch the last service number due to the error {result}, query {query}"
                return

            if result is None:
                self.errors['service_number_query'] = f"the result is empty"
                return

            self.service_number = result[0] + 1
            logger.debug(f"")
        except Exception as e:
            logger.debug(f"[GET-LAST-SERVICE-NUMBER] - {e}")

    def __get_start_date(self):
        success = False
        try:
            query = f"select to_char(to_date(start_date), 'MM/DD/yyyy') from {self.SCHEMA}.sis_academic_calendar " \
                    f"where semester ={self.current_semester} and ITEM_CODE=3 "

            result = self.oracle.select(query, fetch='one')
            if result:
                success = True

            logger.debug(f"[GET-START-DATE] query status - {success}, result - {result}")

            if not success:
                self.errors[
                    'query_get_start_date'] = f"failed to fetch the start date due to the error {result}, query {query}"
                return

            if result is None:
                self.errors['query_get_start_date'] = f"the result is empty"
                return

            self.start_date = result[0]
        except Exception as e:
            logger.debug(f"[GET-START-DATE][EXCEPTION] - {e}")

    def __get_applicant_process_id(self, national_id):
        success = False
        query = f"SELECT PROCESS_ID FROM {self.SCHEMA}.SIS_APPLICATIONS WHERE NATIONAL_ID='{national_id}'"

        result = self.oracle.select(query, fetch='one')
        if result:
            success = True

        logger.debug(f"[PAYMENT-PUSH-SERVICE][GET-APPLICANT-PROCESS-ID] query status - {success}, result - {result}")

        if not success:
            self.errors['query_applicant_process_id'] = \
                f"failed to fetch the applicant process id due to the error {result}, query {query}"
            return

        if result is None:
            self.errors['query_applicant_process_id'] = f"the result is empty"
            return

        self.applicant_process_id = result[0]

    def __get_update_voucher_types(self):

        # update table voucher types
        GS_VOUCHER_TYPES_UPDATE = f"UPDATE {self.SCHEMA}.GS_VOUCHER_TYPES SET LAST_SERIAL = LAST_SERIAL + 1 WHERE " \
                                  f"VOUCHER_TYPE=2 "

        success = self.oracle.update(GS_VOUCHER_TYPES_UPDATE)
        message = None

        logger.debug(
            f"[SELECT-UPDATE-VOUCHER-TYPES] query status - {success}, result - {message}")

        if not success:
            logger.debug(f"[SELECT-UPDATE-VOUCHER-TYPES] fail to update data:"
                         f" {message}, query {GS_VOUCHER_TYPES_UPDATE}")

            self.errors[
                'update_voucher_type'] = \
                f"failed to update GS_VOUCHER_TYPES due to error : {message}, query {GS_VOUCHER_TYPES_UPDATE}"

            return

        # select updated field
        query = f"SELECT LAST_SERIAL FROM {self.SCHEMA}.GS_VOUCHER_TYPES WHERE VOUCHER_TYPE=2"

        result = self.oracle.select(query, fetch='one')
        message = None

        logger.debug(f"[SELECT-UPDATE-VOUCHER-TYPES] query status - {success}, result - {result}")

        if not success:
            logger.debug(f"[SELECT-UPDATE-VOUCHER-TYPES] fail to select data: {message}, query {query}")

            self.errors['select_voucher_types'] = \
                f"failed to select GS_VOUCHER_TYPE due to error : {message}, query {query}"

            return

        if result is None:
            self.errors['select_voucher_types'] = f"the result is empty"
            return

        return result[0]

    def __get_update_sas_voucher_types(self):

        # update table sas voucher types
        update_query = f"UPDATE {self.SCHEMA}.SAS_VOUCHER_TYPES SET LAST_SERIAL = LAST_SERIAL + 1 WHERE " \
                       f"VOUCHER_TYPE=2 "

        success = self.oracle.update(update_query)
        message = None

        logger.debug(f"[SELECT-UPDATE-SAS_VOUCHER_TYPES] query status - {success}, result - {message}")

        if not success:
            logger.debug(f"[UPDATE-SAS_VOUCHER_TYPES] fail to update data: {message}, query {update_query}")

            self.errors['select_update_sas_voucher_type'] = \
                f"failed to update SAS_VOUCHER_TYPES due to error: {message} , query {update_query}"

            return

        # get updated field
        query = f"SELECT LAST_SERIAL FROM {self.SCHEMA}.SAS_VOUCHER_TYPES WHERE VOUCHER_TYPE=2"
        success = False
        result = self.oracle.select(query, fetch='one')
        if result:
            success = True

        logger.debug(f"[SELECT-SAS_VOUCHER_TYPES] query status - {success}, result - {result}")

        if not success:
            logger.debug(f"[SELECT-UPDATE-SAS_VOUCHER_TYPES] fail to select data: {result}, query {query}")

            self.errors['select_update_sas_voucher_type'] = \
                f"failed to select SAS_VOUCHER_TYPE due to error: {result}, query {query}"
            return

        if result is None:
            self.errors['select_update_sas_voucher_type'] = f"the result is empty"
            return

        return result[0]

    def __get_transaction_code(self, applicant_id, fees_code):
        success = False
        query = """SELECT SERIAL FROM {}.SAS_STUDENT_CLAIMS WHERE STUDENT_ID={} AND SEMESTER = {} AND FEES_CODE={}
                ORDER BY LAST_UPDATE_DATE DESC""".format(
            self.SCHEMA, str(applicant_id), str(self.current_semester), str(fees_code))

        result = self.oracle.select(query, fetch='one')
        logger.debug(f"[RESULT] : __get_transaction_code -  {result}")
        if result:
            success = True

        if not success:
            logger.debug(f"[SELECT-TRANS-SEQ]{result}, But Value Set as `1`")

            # self.errors['select_trans_code'] = f"failed to fetch trans-seq-code to error {result}, Value Set as `1`"
            return 1

        logger.debug(f"[SELECT-TRANS-SEQ] query status {success}, result {result}")
        return result[0] + 1

    def __insert_sis_student_service(self, data):

        query = """INSERT INTO {0}.SIS_STUDENT_SERVICES(
                  "SEMESTER", "SERVICE_NO", "STUDENT_ID", "TRANS_CODE", "REQUEST_DATE",
                  "REQUESTED_BY", "EXPECTED_DATE", "IS_SERVED", "COMPANY_ID", "VOUCHER_TYPE",
                  "VOUCHER_EDITION", "VOUCHER_NO" ) 
                  VALUES 
                  ({1},{2},{3},{4}, sysdate ,407 , sysdate , 0 , 1 , 2 ,'B',{5})""".format(
            self.SCHEMA,
            str(self.current_semester),
            str(self.service_number),
            str(data["app_applicant_id"]),
            str(data["trans_code"]),
            str(data["gs_voucher_type"]))

        success = self.oracle.insert(query)
        message = None

        if not success:
            logger.debug(
                f"[INSERT-SIS_STUDENT_SERVICES] fail to insert data: {message}, query - {query}")

            self.errors['insert_sis_student_service'] = \
                f"failed to insert SIS_STUDENT_SERVICES due to error: {message} - query {query}"
            return

        logger.debug(f"[INSERT-SIS_STUDENT_SERVICES] query status - {success}, result - {message}")

    def __insert_sas_vouchers(self, data):

        COLUMNS = """ 
            "COMPANY_ID", "VOUCHER_TYPE", "VOUCHER_EDITION", "VOUCHER_NO", "NOTES", "VOUCHER_DATE","CURR_AMT",
            "CURR_CODE", "BASE_AMT", "CASH_AMT", "CHECK_AMT", "CLAIM_AMT", "SYSTEM_ID", "CUSTOMER_TYPE", "CUSTOMER_ID",
            "CUSTOMER_NAME", "SEMESTER", "STATUS", "PRINT_COUNT", "ENTRY_DATE", "USER_ID", "TRANSFER_AMT", "IS_DEPOSIT",
            "DEPOSIT_CASH_AMT", "DEPOSIT_CHECK_AMT", "IS_BEFOREHAND", "CREDIT_CARD_AMT", "CREDIT_CARD_NET",
            "NUMBER_OF_MONTH", "SEMESTER_DATE", "CREDIT_CODE", "ADMISSION_NOTE", "ADMISSION_NOTE_S" """

        VALUES = f"""
            1 , 2 , 'B' , {str(data['sas_voucher_type'])}, '{str(data['note'])}', sysdate , {str(data["amount"])}, 1,
            {str(data["amount"])} , 0, 0 , {str(data["amount"])} , 1 , 10 , {str(data["app_applicant_id"])},
            '{str(data["app_applicant_name"])}', {str(self.current_semester)}, 1 , 0 , sysdate , 407 , 0 , 0 , 0 , 0 ,
            0 , {str(data["credit_amount"])} , 0, 5 , TO_DATE('{str(self.start_date)}', 'MM/DD/yyyy'),
            {str(data['credit_code'])},'{str(data['admission_note'])}', '{str(data['admission_note_s'])}'
        """

        query = f""" INSERT INTO {self.SCHEMA}.SAS_VOUCHERS({COLUMNS}) VALUES ({VALUES}) """

        success = self.oracle.insert(query)
        message = None

        if not success:
            logger.debug(f"[INSERT-SAS_VOUCHERS] fail to insert data: {message}, query - {query}")

            self.errors['insert_sas_vouchers'] = f"failed to insert SAS_VOUCHERS : {message} , query - {query}"
            return

        logger.debug(f"[INSERT-SAS_VOUCHERS] query Status {success}, result {message}")

    def __insert_sas_student_claims(self, data):

        query = f"""
        INSERT INTO {self.SCHEMA}.SAS_STUDENT_CLAIMS( "STUDENT_ID","SEMESTER", "FEES_CODE", "SERIAL", "FEES_AMT", 
        "EXEMPTION_AMT", "OLD_FEES_AMT", "SERVICE_NO", "ENTER_BY_USER", "CLAIM_DATE", "COMPANY_ID", "LAST_UPDATE_DATE", 
        "ENTRY_DATE", "FACULTY_NO", "MAJOR_NO","CAMPUS_NO", "VAT_AMT", "VATOUT_EXEMPTION_AMT", "STUDY_CODE", 
        "IS_REDUCED")  
        VALUES ({str(data["app_applicant_id"])}, {str(self.current_semester)}, {str(data['fees_code'])},
        {str(data['trans_seq'])}, {str(data["old_fees_amount"])}, 0, {str(data["old_fees_amount"])},
        {str(self.service_number)}, 407, sysdate, 1,  sysdate, sysdate, NULL, NULL, NULL, {str(data['vat'])}, 0, NULL, 0)
        """
        success = self.oracle.insert(query)

        if not success or re.search(r'ORA', str(success)):
            try:
                logger.debug(f"[INSERT-SAS_STUDENT_CLAIMS] fail to insert data: {success}, query-{query}")

                self.errors['insert_sas_student_claims'] = \
                    f"failed to insert SAS_STUDENT_CLAIMS: {str(success)}, query-{query}"
                return
            except Exception as e:
                logger.debug(f"[EXCEPTION][__insert_sas_student_claims] - {e}")

        logger.debug(f"[INSERT-SAS_STUDENT_CLAIMS] query status - {success}")
        return

    def __update_vat_sas_student_claims(self, data):
        query = f"""SELECT * FROM {self.SCHEMA}.SAS_STUDENT_CLAIMS WHERE STUDENT_ID={str(data["app_applicant_id"])} AND
                SEMESTER= {str(self.current_semester)} AND FEES_CODE={str(data['fees_code'])} """

        success = self.oracle.select(query, fetch='one')
        message = None

        logger.debug(f"[INSERT-SAS_VAT_STUDENT_CLAIMS] query status {success}")

        if not success:
            insert_query = """
            INSERT INTO {0}.SAS_STUDENT_CLAIMS("STUDENT_ID","SEMESTER", "FEES_CODE", "SERIAL", "FEES_AMT",
            "EXEMPTION_AMT", "CLAIM_DATE", "COMPANY_ID", "LAST_UPDATE_DATE", "ENTRY_DATE", "STUDY_CODE", "IS_REDUCED"
            ) 
            VALUES ({1}, {2}, {3}, {4}, {5}, 0, sysdate, 1, sysdate, sysdate, 0, 0)""".format(
                self.SCHEMA, str(data["app_applicant_id"]), str(self.current_semester), str(data['fees_code']),
                str(data['trans_seq']), str(data["vat_amount"]),
            )

            results = self.oracle.insert(insert_query)
            logger.info(f"[INSERT][SAS_STUDENT_CLAIMS] result  {results} ,query {insert_query}")

        else:
            success = False
            select_query = f"""
            SELECT FEES_AMT FROM {self.SCHEMA}.SAS_STUDENT_CLAIMS WHERE
            STUDENT_ID={str(data["app_applicant_id"])} AND SEMESTER= {str(self.current_semester)} 
            AND FEES_CODE={str(data['fees_code'])} """

            select_message = self.oracle.select(select_query, fetch='one')
            if select_message:
                success = True
            logger.debug(f"[SELECT] query status - {success}, result - {select_message}")

            if not success:
                logger.debug(f"[SAS_STUDENT_CLAIMS] fail to Select data:  query - {select_query}")

                self.errors['select_sas_student_claims'] = f"failed to insert GS_VOUCHERS : {message} - query {query}"

            fees_amt = int(select_message[0]) + data["vat_amount"]

            update_query = f""" UPDATE {self.SCHEMA}.SAS_STUDENT_CLAIMS
                                SET FEES_AMT = {str(fees_amt)}, LAST_UPDATE_DATE = SYSDATE
                                WHERE STUDENT_ID={str(data["app_applicant_id"])} AND
                                SEMESTER= {str(self.current_semester)} AND FEES_CODE=30 """

            success = self.oracle.update(update_query)
            logger.debug(f"[UPDATE][SAS_STUDENT_CLAIMS] query status - {success}")

            if not success:
                logger.debug(f"[SAS_STUDENT_CLAIMS] fail to Update data:  query - {update_query}")

                self.errors['update_sas_student_claims'] = f"failed to insert GS_VOUCHERS : {success} - query {query}"
        return

    def __insert_gs_vouchers(self, data, services=True):

        query = """ INSERT INTO {0}.GS_VOUCHERS(
                    "COMPANY_ID", "VOUCHER_TYPE", "VOUCHER_EDITION", "VOUCHER_NO", "SYSTEM_ID",
                    "ACCOUNT_TYPE", "CUSTOMER_TYPE", "CUSTOMER_ID",
                    "VOUCHER_DATE", "CURR_CODE" , "VOUCHER_AMT", "BASE_AMT", "STATUS",
                    "USER_ID", "SEMESTER", "RELATED_ISSUE", "PAYMENT_AMT", "SAS_VOUCHER_TYPE",
                    "SAS_VOUCHER_EDITION", "SAS_VOUCHER_NO", "NOTE", "NOTE_S") 
                    VALUES (1 , 2 , 'B' , {1} , 1 , {2} , 10 , {3} , sysdate , 1 , {4} , {5} , 1 , 407 , {6} ,
                    '{7}' , {8} , 2 , 'B', {9}, '{10}', '{11}')""".format(
            self.SCHEMA, str(data['gs_voucher_type']), 1 if services else 2, str(data["app_applicant_id"]),
            str(data["amount"]), str(data["amount"]), str(self.current_semester),
            str(self.current_semester) + "/" + str(data['fees_code']) + "/" + str(data['trans_seq']),
            str(data["amount"]), str(data['sas_voucher_type']),
            str(data["note"]), str(data["note_s"])
        )

        success = self.oracle.insert(query)

        if not success:
            logger.debug(f"[GS_VOUCHERS] fail to insert data: {success}, query {query}")

            self.errors['insert_gs_vouchers'] = f"failed to insert GS_VOUCHERS : {success}, query - {query}"
            return

        logger.debug(f"[INSERT-GS_VOUCHERS] query status - {success}")
        return

    def __insert_sas_credit_card_payments(self, data):

        query = """ INSERT INTO {0}.SAS_CREDIT_CARD_PAYMENTS(
                    "COMPANY_ID", "VOUCHER_TYPE", "VOUCHER_EDITION", "VOUCHER_NO", "CURR_AMT",
                    "CHARGE_PERCENT", "NET_AMT", "ENTRY_USER",
                    "ENTRY_DATE", "CREDIT_CODE" , "DUE_DATE") 
                    VALUES (1 , 2 , 'B' , {1} , {2} , 0 , {3} , 407, sysdate , {4} , sysdate)""".format(
            self.SCHEMA, str(data['voucher_type']), str(data["paid_amount"]), str(data["paid_amount"]),
            str(data["credit_code"]),
        )

        success = self.oracle.insert(query)

        if not success:
            logger.debug(f"[SAS_CREDIT_CARD_PAYMENTS] fail to insert data: {success}, query - {query}")

            self.errors['insert_sas_credit_cart_payments'] = \
                f"failed to insert SAS_CREDIT_CARD_PAYMENTS : {success} - query {query}"
            return

        logger.debug(f"[INSERT-SAS_CREDIT_CARD_PAYMENTS] query status - {success}")

    # ------------------------------------------------------------------------------------------------------------------

    # Push Hyperpay Oracle Process
    def payment_oracle_update(self, checkout, applicant):
        try:
            """
                send all services that already saved to E-register after finish the processing
            """
            logger.debug("Starting to push services payments........")

            national_id = applicant.national_id
            apply_semester = applicant.apply_semester
            full_name = applicant.arabic_full_name
            amount = checkout.amount
            fees_code = checkout.payment_id.code
            amount_vat = checkout.amount - checkout.payment_id.cost
            # payment_gateway=checkout.gateway
            payment_gateway = 1

            logger.debug(f"amount - {amount}, fee code - {fees_code}, amount vat - {amount_vat}")

            self.__get_applicant_process_id(national_id)

            if self.errors.__len__() > 0:
                return self.errors

            sas_voucher_type = self.__get_update_sas_voucher_types()

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                return self.errors
            logger.debug(f"[SAS_VOUCHER_TYPE] : UPDATE SAS_VOUCHER_TYPE Value : {sas_voucher_type}")

            # INSERT into table sas vouchers
            self.__insert_sas_vouchers(
                {
                    "app_applicant_id": str(apply_semester) + str(self.applicant_process_id),
                    "app_applicant_name": full_name,
                    "sas_voucher_type": sas_voucher_type,
                    "amount": amount,
                    "credit_amount": amount,
                    "credit_code": payment_gateway,
                    "admission_note": "السند مقابل رسوم القبول",
                    "admission_note_s": "This Voucher against the admission fees",
                    "note": f"{'منصة - بطاقة إئتمانية' if payment_gateway == '1' else 'منصة - بطاقة مدى '}" +
                            " (" + str(checkout.transaction_id) + ")"
                }
            )

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                return self.errors
            logger.debug(f"[SAS_VOUCHERS] : INSERTION DONE!! to SAS_VOUCHERS")

            self.__insert_sas_credit_card_payments(
                {
                    "voucher_type": sas_voucher_type,
                    "paid_amount": amount,
                    "credit_code": payment_gateway
                }
            )

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                return self.errors
            logger.debug(f"[SAS_CREDIT_CARD_PAYMENTS] : INSERTION DONE!! to SAS_CREDIT_CARD_PAYMENTS")

            # GET the latest service number fom table : SAS_STUDENT_CLAIMS
            self.__get_service_number()

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                return self.errors
            logger.debug(f"[MAX SERVICE_NO] : GET MAX SERVICE_NO Value : {self.service_number}")

            gs_voucher_type = self.__get_update_voucher_types()

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                return self.errors
            logger.debug(f"[GS_VOUCHER_TYPE] : GET GS_VOUCHER_TYPE Value : {gs_voucher_type}")

            # prepare default data
            data = {
                "app_applicant_id": str(apply_semester) + str(self.applicant_process_id),
                "app_applicant_name": full_name,
                "trans_code": checkout.payment_id.Trans_code,
                "fees_code": fees_code,
                "sas_voucher_type": sas_voucher_type,
                "gs_voucher_type": gs_voucher_type,
                "amount": amount,
                "note": str(checkout.transaction_id),
                "note_s": str(checkout.transaction_id),

            }

            # INSERT into table sis student service
            self.__insert_sis_student_service(data)

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                return self.errors
            logger.debug(f"[SIS_STUDENT_SERVICE] : INSERTION DONE!! to SIS_STUDENT_SERVICE")

            # GET transaction seq
            trans_seq = self.__get_transaction_code(str(apply_semester) + str(self.applicant_process_id), fees_code)

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                logger.debug(f"[TRANSACTION_CODE]: [ERROR]!! {self.errors.__len__()} ")
                return self.errors

            logger.debug(f"[TRANS_SEQ] - GET TRANS-SEQ CODE - {trans_seq}")

            # insert into table gs vouchers
            self.__insert_gs_vouchers(
                {
                    **data,
                    "fees_code": fees_code,
                    "trans_seq": trans_seq,
                    "amount": amount
                }
            )

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                return self.errors
            logger.debug(f"[GS_VOUCHERS] : INSERTION DONE!! TO GS_VOUCHERS")

            # INSERT into sas student claims
            self.__insert_sas_student_claims({
                **data,
                "vat": amount_vat,
                "old_fees_amount": amount,
                "trans_seq": trans_seq,
            })

            # check if it has an error, then return errors
            if self.errors.__len__() > 0:
                logger.debug(f"[SAS-STUDENT-CLAIMS]: [ERROR]!! {self.errors.__len__()}")
                return self.errors
            logger.debug(f"[SAS_STUDENT_CLAIM] : INSERTION DONE!! TO SAS_STUDENT_CLAIM")

            if national_id[0] != '1':
                vat_amount = (int(amount) * (15 / 100))
                gs_voucher_no = self.__get_update_voucher_types()

                # check if it has an error, then return errors
                if self.errors.__len__() > 0:
                    return self.errors
                logger.debug(f"[GS_VOUCHER_TYPE] : GET GS_VOUCHER_TYPE Value : {gs_voucher_type}")

                # insert or update into sas student claims
                self.__update_vat_sas_student_claims({
                    **data,
                    "vat": amount_vat,
                    "old_fees_amount": amount,
                    "vat_amount": amount_vat,
                    "trans_seq": trans_seq,
                    "fees_code": 30
                })
                self.__insert_gs_vouchers(
                    {
                        **data,
                        "gs_voucher_type": gs_voucher_no,
                        "amount": vat_amount,
                        "trans_seq": 1,
                        "fees_code": 30,
                    }
                )
            return True

        except Exception as e:
            logger.debug(f"[EXCEPTION] : {e}")
