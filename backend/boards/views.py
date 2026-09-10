from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework import status as http_status
from rest_framework.response import Response
from .models import Board, Task
from .serializers import BoardSerializer, TaskSerializer


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer

    def get_queryset(self):
        # изоляция: user видит только свои доски
        return Board.objects.filter(owner=self.request.user)

    # perform_create нужен для того, чтобы, например, при создании новой доски
    # пользователь не указал в теле запроса {author: 1, ...} и не смог создать доску от лица 
    # другого человека. Поэтому когда роутер видит запрос типа POST api/boards/ он берет access токен 
    # человека, отправляющео запрос и автоматически вставляет его в сериализатор
    def perform_create(self, serializer): # а еще preform_create просто немного дополняет обычный create из линейки 5 миксинов (list(), retrieve(), update() и т.д.)
        # владелец берется из токена, а не из тела запроса 
        serializer.save(owner=self.request.user)
    

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        order = request.data.get('order', [])
        new_status = request.data.get('status')

        tasks = Task.objects.filter(
            id__in=order, board__owner=request.user
        )
        task_map = {t.id: t for t in tasks}

        to_update = []
        for index, task_id in enumerate(order):
            task = task_map.get(task_id)
            if not task:
                continue
            task.position = index
            if new_status:
                task.status = new_status
            to_update.append(task)

        # одним запросом обновляем позиции (и статус) всех задач колонки
        Task.objects.bulk_update(to_update, ["position", "status"])
        return Response({"updated": len(to_update)}, status=http_status.HTTP_200_OK)

    def get_queryset(self):
        # только задачи из досок текущего пользователя
        qs = Task.objects.filter(board__owner=self.request.user)
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        # проверка принадлежности доски пользователю
        if board.owner != self.request.user:
            raise PermissionDenied("Это не ваша доска")
        serializer.save()


