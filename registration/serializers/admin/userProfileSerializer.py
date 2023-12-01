from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from registration.models.user_model import User


class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=False,
                                     style={'input_type': 'password', 'placeholder': 'New Password'})

    class Meta:
        model = User
        fields = ('full_name', 'Phone', 'password',)

    def update(self, instance, validated_data):
        instance.full_name = validated_data['full_name']
        instance.Phone = validated_data['Phone']

        if 'password' in validated_data and validated_data['password'] is not None:
            instance.password = make_password(validated_data['password'])

        instance.save()
        return instance
