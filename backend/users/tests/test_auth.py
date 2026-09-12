import pytest
from django.contrib.auth.models import User


'''
@pytest.mark.django_db - дает тестам внутри доступ к БД
'''

@pytest.mark.django_db
class TestRegistration:
    def test_register_success(self, api_client):
        resp = api_client.post('/api/auth/register/', {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 201
        assert User.objects.filter(username="newuser").exists()

    def test_password_is_hashed(self, api_client):
        api_client.post('/api/auth/register/', {
            'username': 'newuser',
            'password': 'SecurePassword12'
        })
        user = User.objects.get(username='newuser')
        assert user.password != 'SecurePassword12'
        assert user.check_password('SecurePassword12')

    def test_register_duplicate_username(self, api_client, user_a):
        ''' проверяем что такое имя уже занято '''
        resp = api_client.post('/api/auth/register/', {
            'username': 'test_user1', 
            'password': 'SomePass12'
        })
        assert resp.status_code == 400

    def test_register_short_password(self, api_client):
        ''' проверяем длину пароля '''
        resp = api_client.post('/api/auth/register/', {
            'username': 'user1', 
            'password': '123'
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_returns_tokens(self, api_client, user_a):
        ''' проверим что JWT токены возвращаются в ответ на логин '''
        resp = api_client.post('/api/auth/login/', {
            'username': 'test_user1', 
            'password': 'SomePass12'
        })
        assert resp.status_code == 200
        assert 'access' in resp.data
        assert 'refresh' in resp.data

    def test_login_wrong_password(self, api_client, user_a):
        resp = api_client.post('/api/auth/login/', {
            'username': 'user1', 
            'password': 'SomePassword123'
        })
        assert resp.status_code == 401

    def test_refresh_token(self, api_client, user_a):
        login = api_client.post('/api/auth/login/', {
            'username': 'test_user1',
            'password': 'SomePass12'
        })
        refresh = login.data['refresh']
        # пытаемся восстановить access через refresh
        resp = api_client.post('/api/auth/refresh/', {'refresh': refresh})
        assert resp.status_code == 200
        assert 'access' in resp.data


@pytest.mark.django_db
class TestProtectedAccess:
    def test_no_token_denied(self, api_client):
        resp = api_client.post('/api/boards/')
        assert resp.status_code == 401

    def test_with_token_allowed(self, api_client, user_a):
        login = api_client.post('/api/auth/login/', {
            'username': 'test_user1', 
            'password': 'SomePass12'
        })
        access = login.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        resp = api_client.get('/api/boards/')
        assert resp.status_code == 200




