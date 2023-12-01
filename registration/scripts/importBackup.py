# import xlrd
# from django.conf import settings
# from django.core.management import call_command
# from django.db import connection
#
# from registration.models.lookup import *
#
#
# def fetchData():
#     if School.objects.all().count() < 1:
#
#         try:
#             file = settings.BASE_DIR / "Sheets/1.xlsx"  # os.path.join(os.path.dirname(os.path.dirname(__file__)), '')
#             excel = xlrd.open_workbook(file)
#
#         except:
#             file = settings.BASE_DIR / "registration/Backup/1.xlsx"  # os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Backup/1.xlsx')
#             excel = xlrd.open_workbook(file)
#
#         # get school data and save into a model
#         readSchools(excel)
#
#         # get university data and save into a model
#         readUniversity(excel)
#
#         # get country data and save into a model
#         readCountries(excel)
#
#         # get city data and save into a model
#         readCities(excel)
#
#     return
#
#
# def readCountries(excel):  # GEN_COUNTRIES
#
#     sheet_countries = excel.sheet_by_index(1)
#     rows_countries = sheet_countries.nrows
#
#     for row in range(1, rows_countries):
#         Country(
#             country_no=int(sheet_countries.cell_value(row, 0)),
#             country_name_arabic=sheet_countries.cell_value(row, 1),
#             country_name_english=sheet_countries.cell_value(row, 2),
#             nationality_arabic=sheet_countries.cell_value(row, 3),
#             nationality_english=sheet_countries.cell_value(row, 4),
#             category_code=sheet_countries.cell_value(row, 6),
#         ).save()
#
#     return
#
#
# def readCities(excel):  # GEN_CITIES
#     sheet_cities = excel.sheet_by_index(2)
#     rows_cities = sheet_cities.nrows
#
#     for row in range(1, rows_cities):
#         city = City(
#             country_no=int(sheet_cities.cell_value(row, 0)),
#             city_no=int(sheet_cities.cell_value(row, 1)),
#             city_name_arabic=sheet_cities.cell_value(row, 2),
#             city_name_englsih=sheet_cities.cell_value(row, 3),
#
#         )
#         if sheet_cities.cell_value(row, 5) not in ['', None]:
#             city.zone_code = int(sheet_cities.cell_value(row, 5))
#
#         city.save()
#     return
#
#
# def readSchools(excel):  # SIS_SCHOOLS
#     sheet_schools = excel.sheet_by_index(0)
#     rows_schools = sheet_schools.nrows
#
#     for row in range(1, rows_schools):
#
#         school = School(
#             school_no=int(sheet_schools.cell_value(row, 0)),
#             school_name_arabic=sheet_schools.cell_value(row, 1),
#             school_name_english=sheet_schools.cell_value(row, 2),
#             city_no=int(sheet_schools.cell_value(row, 8))
#         )
#         if sheet_schools.cell_value(row, 7) not in ['', None]:
#             school.country_no = int(sheet_schools.cell_value(row, 7))
#
#         if sheet_schools.cell_value(row, 9) not in ['', None]:
#             school.school_type = int(sheet_schools.cell_value(row, 9))
#
#         school.save()
#     return
#
#
# def readUniversity(excel):  # SIS_UNIVERSITIES
#     sheet_universities = excel.sheet_by_index(3)
#     rows_universities = sheet_universities.nrows
#
#     for row in range(1, rows_universities):
#         univ = University(
#             university_code=int(sheet_universities.cell_value(row, 0)),
#             university_name_arabic=sheet_universities.cell_value(row, 1),
#             university_name_english=sheet_universities.cell_value(row, 2)
#         )
#         if sheet_universities.cell_value(row, 3) not in ['', None]:
#             univ.country_code = int(sheet_universities.cell_value(row, 3))
#
#         if sheet_universities.cell_value(row, 17) not in ['', None]:
#             univ.university_type = int(sheet_universities.cell_value(row, 17))
#
#         univ.save()
#
#     return
#
#
# # GEN_COUNTRY_ZONES for school zones
#
#
# def importBckup():
#     cursor = connection.cursor()
#
#     stmt_tables = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name in (" \
#                   "'registration_nationality','registration_city','registration_school','registration_university')) "
#     cursor.execute(stmt_tables)
#     result = cursor.fetchone()[0]
#     if result:
#         # prepare Countries
#         readCountries(cursor, excel)
#
#         # prepare cities
#         readCities(cursor, excel)
#
#         # prepare schools
#         readSchools(cursor, excel)
#
#         # prepare university
#         readUniversity(cursor, excel)
#
#     else:
#         call_command("migrate", interactive=False)
# #
