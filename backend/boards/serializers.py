from rest_framework import serializers
from .models import Board, Task


class BoardSerializer(serializers.ModelSerializer):
    '''
    здесь нет owner в полях. Мы не даем клиенту его передавать: владельца проставим
    на сервере из токена. Иначе злоумышленник мог бы создать доску от чужого имени, 
    просто подставив чужой owner в JSON
    '''
    class Meta:
        model = Board
        fields = ('id', 'title', 'created_at')
        read_only_fields = ('id', 'created_at')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'board', 'title', 'status', 'due_date', 'created_at')
        read_only_fields = ('id', 'created_at')

        