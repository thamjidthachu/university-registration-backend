from rest_framework import serializers
from ...models.user_model import User


class RoomListUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'full_name', 'role', 'gender',)
