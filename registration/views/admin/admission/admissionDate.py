from django.utils.timezone import datetime
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.models.applicant import Reservation
from registration.models.evaluation import Interview, EnglishTest
from registration.models.user_model import User
from registration.serializers.admin.admissionSerializer import SetDateSerializer, DateListSerializer, \
    UpdateDateSerializer
from registration.serializers.admin.englishGradeSerializer import EnglishListSerializer
from registration.serializers.admin.interviewGradeSerializer import InterviewListSerializer
from registration.signals.reservation import Signal


class AdmissionDate(GenericAPIView):
    cache_type_prefix = "admission_"
    cache_date_prefix = "admission_date_"

    def get(self, request, type):
        if type in ['english', 'interview']:
            gender = self.request.query_params.get('gender', None)
            dates = self.get_date_applicants(1 if type == "english" else 2, gender)
            no_date_msg_ar = "لا توجد تواريخ باللغة الإنجليزية" if type == 'english' else 'لا توجد مواعيد مقابلة'

            if dates is not None:
                return Response(dates, status=HTTP_200_OK)

            return Response({"warning": f"No {type} Dates Found", "warning_ar": no_date_msg_ar}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"type": "Invalid type", "type_ar": "نوع غير صحيح"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if kwargs['type'] == 'save':
            test_type = None
            if isinstance(self.request.data, list):
                for data in self.request.data:
                    test_type = data['test_type']
                    set_dates = SetDateSerializer(data=data)
                    set_dates.is_valid(raise_exception=True)
                    set_dates.save(user=self.get_user(int(self.request.session['user']['pk'])))
            else:
                test_type = self.request.data['test_type']
                set_dates = SetDateSerializer(data=self.request.data)
                set_dates.is_valid(raise_exception=True)
                set_dates.save(user=self.get_user(int(self.request.session['user']['pk'])))

            dates = self.get_date_applicants(test_type)
            no_date_msg_ar = "لا توجد تواريخ باللغة الإنجليزية" if test_type == 'english' else 'لا توجد مواعيد مقابلة'

            if dates is not None:
                return Response(dates, status=HTTP_200_OK)
            return Response({"warning": f"No {test_type} Dates Found", "warning_ar": no_date_msg_ar}, status=HTTP_400_BAD_REQUEST)
        return Response({"error": "Not found", "error_ar": "لا يوجد"}, status=HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        if kwargs['type'] == 'update':
            update = UpdateDateSerializer(data=self.request.data)
            update.is_valid(raise_exception=True)
            update.validated_data['user'] = self.get_user(int(self.request.session['user']['pk']))
            update.update(update.validated_data['reservation'], update.validated_data)
            dates = self.get_date_applicants(update.validated_data['test_type'])
            no_date_msg_ar = "لا توجد تواريخ باللغة الإنجليزية" if update.validated_data['test_type'] == 'english' else 'لا توجد مواعيد مقابلة'
            if dates is not None:
                return Response(dates, status=HTTP_200_OK)

            return Response({"warning": f"No {update.validated_data['test_type']} Dates Found", "warning_ar": no_date_msg_ar}, status=HTTP_400_BAD_REQUEST)

        return Response({"error": "Not found"}, status=HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        if kwargs['type'] == 'delete':
            deleted_date = Reservation.objects.get(pk=self.request.data['id'])
            test_type = deleted_date.test_type
            if deleted_date.reserved:
                return Response({"date": "Error! This date already reserved!", "date_ar": "هذا الموعد تم حجزه بالفعل"},
                                status=HTTP_400_BAD_REQUEST)

            deleted_date.delete()

            dates = self.get_date_applicants(test_type)
            if dates is not None:
                return Response(dates, status=HTTP_200_OK)

            return Response([], status=HTTP_200_OK)

        return Response({"error": "Not found", "error_ar": "لا يوجد"}, status=HTTP_404_NOT_FOUND)

    @staticmethod
    def get_reservations(date_type, gender):
        reservations = Reservation.objects.filter(
            test_type=date_type,
            reservation_date__gte=(datetime.now().date())
        ).order_by("reservation_date")
        if gender:
            reservations = reservations.filter(gender=gender)

        return reservations

    @staticmethod
    def get_user(pk):
        return User.objects.get(id=pk)

    def get_date_applicants(self, date_type, gender=None):

        self.cache_date_prefix += "english" if int(date_type) == 1 else "interview"

        cache_date_model = self.cache_date_prefix + "_" + (gender + "_" if gender else "") + "_model"
        cache_date_serializer = self.cache_date_prefix + "_" + (gender + "_" if gender else "") + "_serializer"

        dates = self.get_data(
            serializer_class=DateListSerializer,
            data=self.get_dates(self.get_reservations, cache_date_model, date_type, gender),
            cache_name=cache_date_serializer
        )

        if len(dates) > 0:

            self.cache_type_prefix += "english" if int(date_type) == 1 else "interview"

            for date in dates:
                if date['test_type'] == "1":
                    cache_type_model = self.cache_type_prefix + "_" + str(date['id']) + "_" + "_model"
                    cache_type_serializer = self.cache_type_prefix + "_" + str(
                        date['id']) + "_" + "_serializer"
                    date['applicants'] = self.get_data_applicants(EnglishListSerializer,
                                                                  data=self.get_english_applicants(
                                                                      EnglishTest.objects.filter,
                                                                      cache_type_model,
                                                                      reservation_id_id=date['id']),
                                                                  cache_name=cache_type_serializer
                                                                  )

                elif date['test_type'] == "2":
                    cache_type_model = self.cache_type_prefix + "_" + str(date['id']) + "_" + "_model"
                    cache_type_serializer = self.cache_type_prefix + "_" + str(
                        date['id']) + "_" + "_serializer"
                    date['applicants'] = self.get_data_applicants(
                        InterviewListSerializer,
                        data=self.get_interview_applicants(Interview.objects.filter, cache_type_model,
                                                           reservation_id_id=date['id']),
                        cache_name=cache_type_serializer
                    )
            return dates
        return

    @staticmethod
    def get_english_applicants(function, cache_name, *args, **kwargs):

        return CacheModel(function=function,
                          params=args,
                          kwargs=kwargs,
                          cache_name=cache_name).get_from_cache()

    @staticmethod
    def get_interview_applicants(function, cache_name, *args, **kwargs):
        return CacheModel(function=function,
                          params=args,
                          kwargs=kwargs,
                          cache_name=cache_name).get_from_cache()

    @staticmethod
    def get_data_applicants(serializer_class, data, cache_name, many=True):
        return CacheSerializer(serializer=serializer_class,
                               data=data,
                               cache_name=cache_name,
                               many=many).get_from_cache()

    def get_dates(self, function, cache_name, *args):
        if Signal.SIGNAL_RESERVATION:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_date_prefix))
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_type_prefix))
            CacheModel.remove_cache(CacheModel.list_filter("applicant_reserve_"))

            Signal.SIGNAL_RESERVATION = False

        return CacheModel(function=function,
                          params=args,
                          cache_name=cache_name
                          ).get_from_cache()

    @staticmethod
    def get_data(serializer_class, data, cache_name, many=True):

        return CacheSerializer(serializer=serializer_class,
                               data=data,
                               cache_name=cache_name,
                               many=many
                               ).get_from_cache()
