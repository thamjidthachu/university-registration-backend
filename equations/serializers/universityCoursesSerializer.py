from rest_framework import serializers
from equations.models.courses import UniversirtyCourse
from registration.models.lookup import University


class UniversityCourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversirtyCourse
        fields = '__all__'


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ('university_name_english', 'university_name_arabic',)
