from rest_framework import serializers
from equations.models.courses import EquivalentCourse
from equations.serializers.universityCoursesSerializer import UniversityCourseDetailSerializer, UniversitySerializer


class ListEquivilantCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquivalentCourse
        exclude = ('user',)

    def to_representation(self, data):
        query = super(ListEquivilantCoursesSerializer, self).to_representation(data)
        query['equivalent_to'] = UniversityCourseDetailSerializer(data.equivalent_to).data
        query['university'] = UniversitySerializer(data.university).data
        return query


class CreatequivilantCoursesSerializer(serializers.ModelSerializer):
    error_msg = {
        "unauthorized": {"error": "You Can't do this action!",
                         "error_ar": "لا يمكنك اضافة مواد."},
        "exists": {"error": "This course already registered.",
                   "error_ar": "هذا المقرر مسجل مسبقاً."}
    }

    class Meta:
        model = EquivalentCourse
        fields = '__all__'

    def validate(self, attrs):
        if attrs['user'].role not in [6, 14]:
            raise serializers.ValidationError(self.error_msg['unauthorized'])

        if EquivalentCourse.objects.filter(**attrs).exists():
            raise serializers.ValidationError(self.error_msg['exists'])

        return attrs
