from registration.scripts.oracle import Oracle
from django.conf import settings
from registration.models.lookup import *
from django.db.models import Q
import logging

logger_oracle = logging.getLogger('root')
logger = logging.getLogger('root')


def import_eregister_data():
    # Get schools from Eregister
    schools = get_schools_data()

    # Get universities from Eregister
    universities = get_universities_data()

    # # Get countries from Eregister
    countries = get_countries_data()

    # # Get cities from Eregister
    cities = get_cities_data()

    return schools and universities and countries and cities


def get_schools_data(DB=settings.ORACLE):
    cur = Oracle()
    query = f"SELECT SCHOOL_NO, SCHOOL_NAME, SCHOOL_NAME_S, COUNTRY_NO, CITY_NO, SCHOOL_TYPE from {DB}.SIS_SCHOOLS"
    schools_data = cur.select(query)
    if not isinstance(schools_data, list):
        logger_oracle.exception(f"Error when adding schools {schools_data}")
        return False
    schools_list_create = []
    schools_list_update = []
    for school in schools_data:
        if 'بدون' not in school and 'غير محدد' not in school and 'غير محدد - أخرى' not in school:
            existing_school = School.objects.filter(Q(school_name_arabic=school[1]) | Q(school_name_english=school[2]))
            if existing_school.exists():
                # if existing_school.count() == 1:
                existing_school = existing_school.last()
                # existing_school.school_name_arabic = school[1]
                # existing_school.school_name_english = school[2]
                existing_school.school_no = school[0]
                existing_school.country_no = school[3]
                existing_school.city_no = school[4]
                existing_school.school_type = school[5]
                schools_list_update.append(existing_school)
                # else: logger_oracle.exception(f"Couldn\'t update school {school[1]} because it exists twice in the
                # Django DB")
            else:
                schools_list_create.append(School(
                    school_no=school[0],
                    school_name_arabic=school[1],
                    school_name_english=school[2],
                    country_no=school[3],
                    city_no=school[4],
                    school_type=school[5]
                ))
    try:
        School.objects.bulk_create(schools_list_create)
        School.objects.bulk_update(schools_list_update, fields=['school_no', 'country_no', 'city_no', 'school_type'])
    except Exception as ex:
        logger_oracle.exception(f"Error in import_ereg_data script when adding School {ex}")
        return False
    return True


def get_universities_data(DB=settings.ORACLE):
    cur = Oracle()
    query = f'SELECT UNIVERSITY_CODE, UNIVERSITY_DESC, UNIVERSITY_DESC_S, COUNTRY_CODE, UNIVERSITY_TYPE from {DB}.SIS_UNIVERSITIES'
    universities_data = cur.select(query)
    if not isinstance(universities_data, list):
        logger_oracle.exception(f"Error when adding universities {universities_data}")
        return False
    universities_list_create = []
    universities_list_update = []
    for univ in universities_data:
        if 'بدون' not in univ and 'غير محدد' not in univ and 'غير محدد - أخرى' not in univ:
            existing_university = University.objects.filter(Q(university_name_arabic=univ[1]) | Q(country_code=univ[2]))
            if existing_university and existing_university.exists():
                # if existing_university.count() == 1:
                existing_university = existing_university.last()
                # existing_university.university_name_arabic = univ[1]
                # existing_university.university_name_english = univ[2]
                existing_university.university_code = univ[0]
                existing_university.country_code = univ[3]
                existing_university.university_type = univ[4]
                universities_list_update.append(existing_university)
                # else: logger_oracle.exception(f"Couldn\'t update university {univ[1]} because it exists twice in
                # the Django DB")
            elif univ[1] != None or univ[2] != None:
                universities_list_create.append(University(
                    university_code=univ[0],
                    university_name_arabic=univ[1],
                    university_name_english=univ[2],
                    country_code=univ[3],
                    university_type=univ[4]
                ))
    try:
        University.objects.bulk_create(universities_list_create)
        University.objects.bulk_update(universities_list_update,
                                       fields=['university_code', 'country_code', 'university_type'])
    except Exception as ex:
        logger_oracle.exception(f"Error in import_ereg_data script when adding University {ex}")
        return False
    return True


def get_countries_data(DB=settings.ORACLE):
    cur = Oracle()
    query = f'SELECT COUNTRY_NO, COUNTRY_NAME, COUNTRY_NAME_S, NATIONALITY, NATIONALITY_S, CATEGORY_CODE from {DB}.GEN_COUNTRIES'
    countries_data = cur.select(query)
    if not isinstance(countries_data, list):
        logger_oracle.exception(f"Error when adding countries {countries_data}")
        return False
    countries_list_create = []
    countries_list_update = []
    for country in countries_data:
        if 'بدون' not in country and 'غير محدد' not in country and 'غير محدد - أخرى' not in country:
            existing_country = Country.objects.filter(
                Q(country_name_arabic=country[1]) | Q(country_name_english=country[2]))
            if existing_country and existing_country.exists():
                # if existing_country.count() == 1:
                existing_country = existing_country.last()
                # existing_country.country_name_arabic = country[1]
                # existing_country.country_name_english = country[2]
                existing_country.country_no = country[0]
                existing_country.nationality_arabic = country[3]
                existing_country.nationality_english = country[4]
                existing_country.category_code = country[5]
                countries_list_update.append(existing_country)
                # else:
                #     logger_oracle.exception(f"Couldn\'t update country {country[1]} because it exists twice in the Django DB")
            elif country[1] != None or country[2] != None:
                countries_list_create.append(Country(
                    country_no=country[0],
                    country_name_arabic=country[1],
                    country_name_english=country[2],
                    nationality_arabic=country[3],
                    nationality_english=country[4],
                    category_code=country[5]
                ))
    try:
        Country.objects.bulk_create(countries_list_create)
        Country.objects.bulk_update(countries_list_update,
                                    fields=['country_no', 'nationality_arabic', 'nationality_english', 'category_code'])
    except Exception as ex:
        logger_oracle.exception(f"Error in import_ereg_data script when adding Country {ex}")
        return False
    return True


def get_cities_data(DB=settings.ORACLE):
    cur = Oracle()
    query = f'SELECT COUNTRY_NO, CITY_NO, CITY_NAME, CITY_NAME_S, ZONE_CODE from {DB}.GEN_CITIES'
    cities_data = cur.select(query)
    if not isinstance(cities_data, list):
        logger_oracle.exception(f"Error when adding cities {cities_data}")
        return False
    cities_list_create = []
    cities_list_update = []
    for city in cities_data:
        if 'بدون' not in city and 'غير محدد' not in city and 'غير محدد - أخرى' not in city:
            existing_city = City.objects.filter(Q(city_name_arabicv=city[2]) | Q(city_name_englsih=city[3]),
                                                country_no=city[0]) if city[0] != None or city[1] != None else None
            if existing_city and existing_city.exists():
                # if existing_city.count() == 1:
                existing_city = existing_city.last()
                # existing_city.city_name_arabic = city[2]
                # existing_city.city_name_englsih = city[3]
                existing_city.city_no = city[1]
                existing_city.zone_code = city[4]
                cities_list_update.append(existing_city)
                # else:
                #     logger_oracle.exception(f"Couldn\'t update city {city[2]} because it exists twice in the Django DB")
            elif city[0] != None or city[1] != None:
                cities_list_create.append(City(
                    country_no=city[0],
                    city_no=city[1],
                    city_name_arabic=city[2],
                    city_name_englsih=city[3],
                    zone_code=city[4]
                ))
    try:
        City.objects.bulk_create(cities_list_create)
        City.objects.bulk_update(cities_list_update, fields=['city_no', 'zone_code'])
    except Exception as ex:
        logger_oracle.exception(f"Error in import_ereg_data script when City School {ex}")
        return False
    return True
