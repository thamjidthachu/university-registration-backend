from rest_framework import serializers
from registration.models.lookup import University


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'
