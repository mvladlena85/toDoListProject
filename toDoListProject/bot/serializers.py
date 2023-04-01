from rest_framework import serializers

from toDoListProject.bot.models import TgUser
from toDoListProject.core.serializers import UserSerializer


class TgUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.SlugField(source='chat_id', read_only=True)
    username = serializers.CharField(source='user.username')

    class Meta:
        model = TgUser
        read_only_fields = ['tg_id', 'user_id', 'verification_code',  'username']
        fields = ['tg_id', 'user_id', 'username', 'verification_code']
