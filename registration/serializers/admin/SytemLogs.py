from rest_framework import serializers

from registration.models.system_log import SystemLog


class SystemLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = ('before_modified', )
