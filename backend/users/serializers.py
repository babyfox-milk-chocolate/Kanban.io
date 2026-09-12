from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    boards_count = serializers.IntegerField(read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'date_joined', 'boards_count', 'tasks_count')
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        # create_user() хеширует пароль. обычный create() сохранил бы пароль в открытом виде
        return User.objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    # аннотированные поля со статистикой (read-only)
    boards_count = serializers.IntegerField(read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)
    avatar = serializers.ImageField(source="profile.avatar", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined", "boards_count", "tasks_count", "avatar")
        read_only_fields = ("id", "date_joined")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("неверный текущий пароль")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user