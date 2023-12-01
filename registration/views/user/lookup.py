import logging

from django.conf import settings
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from registration.scripts.oracle import Oracle

logger_oracle = logging.getLogger('root')
logger = logging.getLogger('root')


class ListLookupView(APIView):

    def get(self, request, *args, **kwargs):
        datas = None

        # Get Lookup type
        lookup = self.request.GET.get('lookup', None)

        if lookup == 'schools':
            datas = self.get_schools_data()
        elif lookup == 'cities':
            datas = self.get_cities_data()
        elif lookup == 'countries':
            datas = self.get_countries_data()
        elif lookup == 'zones':
            datas = self.get_zones_data()

        return Response(datas, status=HTTP_200_OK)

    def get_schools_data(self, Schema=settings.ORACLE):
        logger.info("Calling get_schools_data")
        cur = Oracle()
        query = f"SELECT SCHOOL_NO, SCHOOL_NAME, SCHOOL_NAME_S, COUNTRY_NO, CITY_NO, SCHOOL_TYPE from {Schema}.SIS_SCHOOLS"
        schools_data = cur.select(query)
        if not isinstance(schools_data, list):
            logger_oracle.exception(f"Error when Fetching schools {schools_data}")
            return False
        schools_list = []
        for school in schools_data:
            schools_list.append({
                'school_no': school[0],
                'school_name_arabic': school[1],
                'school_name_english': school[2],
                'country_no': school[3],
                'city_no': school[4],
                'school_type': school[5]
            })
        return schools_list

    def get_zones_data(self, Schema=settings.ORACLE):
        cur = Oracle()
        query = f'SELECT ZONE_CODE, ZONE_NAME, ZONE_NAME_S, COUNTRY_NO from {Schema}.GEN_COUNTRY_ZONES'
        zones_data = cur.select(query)
        if not isinstance(zones_data, list):
            logger_oracle.exception(f"Error when Fetching Zones {zones_data}")
            return False
        zones_list = []
        for zone in zones_data:
            zones_list.append({
                'zone_code': zone[0],
                'zone_name_arabic': zone[1],
                'zone_name_english': zone[2],
                'country_no': zone[3],
            })
        return zones_list

    def get_cities_data(self, Schema=settings.ORACLE):
        cur = Oracle()
        query = f'SELECT COUNTRY_NO, CITY_NO, CITY_NAME, CITY_NAME_S, ZONE_CODE from {Schema}.GEN_CITIES'
        cities_data = cur.select(query)
        if not isinstance(cities_data, list):
            logger_oracle.exception(f"Error when Fetching cities {cities_data}")
            return False
        cities_list = []
        for city in cities_data:
            cities_list.append({
                'country_no': city[0],
                'city_no': city[1],
                'city_name_arabic': city[2],
                'city_name_english': city[3],
                'zone_code': city[4]
            })
        return cities_list

    def get_countries_data(self, Schema=settings.ORACLE):
        cur = Oracle()
        query = f'SELECT COUNTRY_NO, COUNTRY_NAME, COUNTRY_NAME_S, NATIONALITY, NATIONALITY_S, CATEGORY_CODE from {Schema}.GEN_COUNTRIES'
        countries_data = cur.select(query)
        if not isinstance(countries_data, list):
            logger_oracle.exception(f"Error when Fetching countries {countries_data}")
            return False
        countries_list = []
        for country in countries_data:
            countries_list.append({
                'country_no': country[0],
                'country_name_arabic': country[1],
                'country_name_english': country[2],
                'nationality_arabic': country[3],
                'nationality_english': country[4],
                'category_code': country[5]
            })
        return countries_list
