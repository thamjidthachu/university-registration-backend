from .major import Major
from .oracle import Oracle
from .NewPayment import PaymentPush
from .oracleProcess import (
    start_major_process, start_payment_process, start_process, store_oracle_process, payment_oracle_process
)
from .checkNationalID import check_national_id
from .import_ereg_data import import_eregister_data
# from .importBackup import fetchData, readCities, readSchools, readUniversity, readCountries
from .newApplicant import NewApplicant
