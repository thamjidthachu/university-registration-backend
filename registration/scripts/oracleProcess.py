from registration.models.oracle_process import OracleProcess, PaymentOracleProcess
from registration.models.applicant import Applicant, Payment
from registration.scripts.major import Major
from registration.scripts.newApplicant import NewApplicant
from registration.scripts.NewPayment import PaymentPush
from django.db.models import Q
from django.utils.timezone import now
import logging

logger = logging.getLogger("oracle_logs")


def store_oracle_process(applicant_id, email, national_id, process):
    try:
        OracleProcess(
            applicant_id=applicant_id,
            email=email,
            national_id=national_id,
            process=process,
        ).save()
        return True

    except Exception as e:
        logger.error('[STORE-ORACLE-PROCESS]' + str(e))
        return e


def payment_oracle_process(applicant_id, payment, process):
    try:
        PaymentOracleProcess(
            applicant_id=applicant_id.id,
            email=applicant_id.email,
            national_id=applicant_id.national_id,
            transaction_id=payment.transaction_id,
            process=process,
        ).save()
        return True

    except Exception as e:
        logger.error('[STORE-PAYMENT-ORACLE-PROCESS]' + str(e))
        return e


def start_process():
    processes = OracleProcess.objects.filter(
        Q(process=1, delivered=False, number_tries__lte=5) | Q(process=2, delivered=False,
                                                               number_tries__lte=5)).order_by('id')
    logger.warn(f'[START-PROCESS-ORACLE] detect {processes.count()}')

    for process in processes:
        applicant = Applicant.objects.filter(Q(id=process.applicant_id, national_id=process.national_id) |
                                             Q(id=process.applicant_id)).last()
        if applicant:
            # if the process is 1 which mean this process will be added applicant to e-register
            if process.process == 1:
                process.send = True
                process.send_date = now()
                process.save()
                logger.info(f'[START-PROCESS-ORACLE-ADD-APPLICANT] add new applicant with id {applicant.id}')
                new = NewApplicant(applicant).new()
                if isinstance(new, bool):
                    process.delivered = True
                    process.delivered_date = now()
                    process.number_tries += 1
                    process.save()
                else:
                    if process.number_tries == 5:
                        process.error_reason = str(new)
                        process.number_tries += 1
                        process.save()
                    else:
                        process.number_tries += 1
                        process.save()
                    return new

            # if the process is 2 which mean this process will be update applicant to e-register
            elif process.process == 2:
                process.send = True
                process.send_date = now()
                process.save()
                logger.info(f'[START-PROCESS-ORACLE-UPDATE-APPLICANT] update applicant with id {applicant.id}')
                update_app = NewApplicant(applicant).update()
                if isinstance(update_app, bool):
                    process.delivered = True
                    process.delivered_date = now()
                    process.number_tries += 1
                    process.save()
                else:
                    if process.number_tries == 5:
                        process.error_reason = str(update_app)
                        process.number_tries += 1
                        process.save()

                    else:
                        process.number_tries += 1
                        process.save()
                    return update_app


def start_major_process():
    processes = OracleProcess.objects.filter(
        Q(process=3, delivered=False, number_tries__lte=5) | Q(process=4, delivered=False, number_tries__lte=5) | Q(
            process=5, delivered=False, number_tries__lte=5)).order_by('id')
    logger.warn(f'[START-PROCESS-MAJOR-ORACLE] detect {processes.count()}')

    for process in processes:
        applicant = Applicant.objects.filter(Q(id=process.applicant_id, national_id=process.national_id) |
                                             Q(id=process.applicant_id)).last()

        if applicant:
            # if the process is 3 which mean this process will be update score to e-register
            if process.process == 3:
                process.send = True
                process.send_date = now()
                process.save()
                logger.info(f'[START-PROCESS-ORACLE-UPDATE-SCORE] update score applicant with id {applicant.id}')
                update_score = NewApplicant(applicant).update_score()
                if isinstance(update_score, bool):
                    process.delivered = True
                    process.delivered_date = now()
                    process.number_tries += 1
                    process.save()
                else:
                    if process.number_tries == 5:
                        process.error_reason = str(update_score)
                        process.number_tries += 1
                        process.save()

                    else:
                        process.number_tries += 1
                        process.save()
                    return update_score

            # if the process is 1 which mean this process will be added Majors to e-register
            elif process.process == 4:
                process.send = True
                process.send_date = now()
                process.save()
                logger.info(f'[START-PROCESS-ORACLE-ADD-MAJOR] add major applicant with id {applicant.id}')
                add_major = Major(applicant).add_major()
                if isinstance(add_major, bool):
                    process.delivered = True
                    process.delivered_date = now()
                    process.number_tries += 1
                    process.save()
                else:
                    if process.number_tries == 5:
                        process.error_reason = str(add_major)
                        process.number_tries += 1
                        process.save()
                    else:
                        process.number_tries += 1
                        process.save()
                    return add_major

            # if the process is 1 which mean this process will be update major to e-register
            elif process.process == 5:
                process.send = True
                process.send_date = now()
                process.save()
                logger.info(f'[START-PROCESS-ORACLE-UPDATE-MAJOR] update major applicant with id {applicant.id}')
                update_major = Major(applicant).update_major()
                if isinstance(update_major, bool):
                    process.delivered = True
                    process.delivered_date = now()
                    process.number_tries += 1
                    process.save()
                else:
                    if process.number_tries == 5:
                        process.error_reason = str(update_major)
                        process.number_tries += 1
                        process.save()
                    else:
                        process.number_tries += 1
                        process.save()
                    return update_major


def start_payment_process():
    processes = PaymentOracleProcess.objects.filter(delivered=False, number_tries__lte=5)
    logger.warn(f'[START-PAYMENT-PROCESS-ORACLE] detect {processes.count()}')

    for process in processes:
        applicant = Applicant.objects.filter(
            Q(id=process.applicant_id, national_id=process.national_id) | Q(id=process.applicant_id)
        ).last()

        if applicant:
            process.send = True
            process.send_date = now()
            process.save()
            logger.info(f'[START-PAYMENT-PROCESS-ORACLE] add new Payment of id {applicant.id}')
            payment = Payment.objects.filter(transaction_id=process.transaction_id).last()
            if payment:
                new = PaymentPush().payment_oracle_update(payment, applicant)
                if isinstance(new, bool):
                    process.delivered = True
                    process.delivered_date = now()
                    process.number_tries += 1
                    process.save()
                else:
                    if process.number_tries == 5:
                        process.error_reason = str(new)
                        process.number_tries += 1
                        process.save()
                    else:
                        process.number_tries += 1
                        process.save()
                    return new
