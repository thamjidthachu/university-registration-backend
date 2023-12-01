from django.db.models import F
from django.db.models import Q
from django.utils.timezone import datetime, timedelta
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.models.applicant import Applicant, Reservation

from ...serializers.user.bookDateSerializer import BookDateSerializer
from ...signals.reservation import Signal


class BookDate(GenericAPIView):
    cache_name_prefix = "applicant_reserve_"

    def get(self, request, *args, **kwargs):
        test_type = kwargs['type']
        no_date_msg_ar = "لا توجد تواريخ باللغة الإنجليزية" if test_type == 'english' else 'لا توجد مواعيد مقابلة'
        if test_type in ['english', 'interview']:
            gender = self.request.query_params.get('gender', None)
            applicant_id = self.request.query_params.get('applicant_id', None)
            applicant = self.get_applicant(applicant_id)
            faculty = applicant.major_id.faculty_id.name

            cache_name_model = self.cache_name_prefix + test_type + "_" + gender if gender else "" + "_model"
            cache_name_serializer = self.cache_name_prefix + test_type + "_" + gender if gender else "" + "_serializer"

            dates = self.get_dates(self.get_reservations,
                                   cache_name_model,
                                   1 if test_type == "english" else 2,
                                   gender,
                                   faculty
                                   )
            if dates.exists():
                all_dates = self.get_data(BookDateSerializer, dates, cache_name_serializer, many=True)
                all_dates = self.handle_dates(all_dates)
                if len(all_dates) > 0:
                    return Response(all_dates, status=HTTP_200_OK)
                else:
                    return Response({"no_dates": f"No {test_type} dates Found", "no_dates_ar": no_date_msg_ar},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response({"no_dates": f"No {test_type} dates Found", "no_dates_ar": no_date_msg_ar},
                                status=HTTP_400_BAD_REQUEST)

        return Response({"ERROR": "Please select type of date", "ERROR_ar": "برجاء اختيار نوع التاريخ"},
                        status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_reservations(test_type, gender, faculty):
        return Reservation.objects.filter(
            Q(faculty='ALL') | Q(faculty=faculty), test_type=test_type, reservation_date__gte=(datetime.now().date()),
            count__lt=F('capacity'), gender=gender
        ).order_by("reservation_date")

    @staticmethod
    def get_applicant(applicant_id):
        return Applicant.objects.get(id=applicant_id)

    @staticmethod
    def handle_dates(dates):
        exclude = []

        for i, dt in enumerate(dates):

            if (datetime.today() - datetime.strptime(str(dt['reservation_date']), "%Y-%m-%d")).days == 0:
                if int(str(dt['start_time']).split(":")[0]) - int(dt['duration_time']) < datetime.now().hour:
                    exclude.append(i)
                elif int(str(dt['start_time']).split(":")[0]) - int(dt['duration_time']) == datetime.now().hour and (
                        int(str(dt['start_time']).split(":")[1]) - datetime.now().minute <= 0):
                    exclude.append(i)
            else:
                diff = str(datetime.strptime(str(dt['reservation_date']) + " " + str(dt['start_time']),
                                             "%Y-%m-%d %H:%M:%S") - timedelta(days=0, hours=int(dt['duration_time']),
                                                                              minutes=0)).split(" ")
                d, t = diff[0], diff[1]
                if (datetime.today() - datetime.strptime(d, "%Y-%m-%d")).days == 0:
                    if (int(t.split(":")[0]) - datetime.now().hour <= 0) and (
                            int(t.split(":")[1]) - datetime.now().minute <= 0):
                        exclude.append(i)

        if len(exclude) > 0:
            for i in range(len(exclude), 0, -1):
                dates.pop(exclude[i - 1])
        return dates

    def get_dates(self, function, cache_name, *args):
        if Signal.SIGNAL_RESERVATION:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_name_prefix))
            Signal.SIGNAL_RESERVATION = False

        return CacheModel(function=function, params=args, cache_name=cache_name).get_from_cache()

    def get_data(self, serializer_class, dates, cache_name, many=True):

        return CacheSerializer(serializer=serializer_class,
                               data=dates,
                               many=many,
                               cache_name=cache_name).get_from_cache()
