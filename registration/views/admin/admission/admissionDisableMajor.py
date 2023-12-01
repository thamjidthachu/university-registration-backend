from datetime import datetime

import pandas as pd
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from cache.cacheModel import CacheModel
from cache.cacheSerializer import CacheSerializer
from registration.models.applicant import Applicant
from registration.models.univStructure import Major
from registration.serializers.admin.admissionSerializer import MajorListSerializer, DisabilityListSerializer
from registration.signals.major import Signal


class AdmissionDisableMajor(GenericAPIView):
    queryset = Major.objects.all()
    cache_prefix = "admission_major"

    def get(self, request, *args, **kwargs):

        cache_name_model = self.cache_prefix + "_model"
        cache_name_serializer = self.cache_prefix + "_serializer"

        return Response(self.get_data(MajorListSerializer,
                                      data=self.get_majors(self.get_queryset, cache_name_model),
                                      cache_name=cache_name_serializer,
                                      many=True), status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):

        for major in self.request.data:
            major_obj = MajorListSerializer(Major.objects.get(id=major['id']), data=major)
            major_obj.is_valid(raise_exception=True)
            major_obj.update(Major.objects.get(name=major['name']),
                             major,
                             int(self.request.session['user']['pk']))

        return Response("Majors Updated", status=HTTP_200_OK)

    def get_majors(self, function, cache_name, *args, **kwargs):
        if Signal.SIGNAL_MAJOR:
            CacheModel.remove_cache(CacheModel.list_filter(self.cache_prefix))
            Signal.SIGNAL_MAJOR = False

        return CacheModel(function=function, cache_name=cache_name, params=args, kwargs=kwargs).get_from_cache()

    def get_data(self, serializer_class, data, cache_name, many=True):
        return CacheSerializer(serializer=serializer_class,
                               data=data,
                               cache_name=cache_name,
                               many=many).get_from_cache()


class AdmissionDisableApplicants(GenericAPIView):
    def get(self, request, *args, **kwargs):
        semester = self.request.query_params.get('semester', None)
        query_set = Applicant.objects.filter(apply_semester=semester).exclude(health_state='ok')
        serializer = DisabilityListSerializer(query_set, many=True)
        serialized_data = serializer.data

        filename = 'Special-Need-Applicants' + datetime.today().strftime("%m/%d/%Y")
        response = HttpResponse(content_type='text/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(filename)
        df = pd.DataFrame.from_dict(serialized_data)
        df.style.set_properties(**{'text-align': 'left', 'font-family': 'Arial', 'font-weight': 'bold'}).to_excel(
            response, index=False)

        return response
