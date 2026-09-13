import pytest 
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from boards.models import Board, Task


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_a(db):
    return User.objects.create_user(username='test_user1', password='SomePass12')

@pytest.fixture
def user_b(db):
    return User.objects.create_user(username='test_user2', password='pass234')

@pytest.fixture
def auth_client_a(api_client, user_a):
    # force_authenticate - хитрость DRF. Логинин клиента без реального прохода через JWT ручку
    # Не надо в каждом тесте дергать /login/, парсить токен, вставлять его в заголовок
    api_client.force_authenticate(user=user_a)
    return api_client

@pytest.fixture
def board_a(user_a):
    return Board.objects.create(owner=user_a, title='test_user1 board')

@pytest.fixture
def board_b(user_b):
    return Board.objects.create(owner=user_b, title='test_user2 board')

@pytest.fixture 
def task_a(board_a):
    return Task.objects.create(board=board_a, title='test_user1 task', status='todo')

@pytest.fixture
def task_b(board_b):
    return Task.objects.create(board=board_b, title="test_user2 task", status="todo")
