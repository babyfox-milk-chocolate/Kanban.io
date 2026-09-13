import pytest
from boards.models import Board


''' 

Здесь возвращаем 404 вместо 403 
Это безопаснее, поскольку атакующий с помощью перебора не сможет понять,
что доска с заданным id вообще существует

'''

@pytest.mark.django_db
class TestBoardCRUD:
    def test_create_board(self, auth_client_a):
        resp = auth_client_a.post('/api/boards/', {'title': 'new_board'})
        assert resp.status_code == 201
        assert resp.data['title'] == 'new_board'

    def test_owner_set_from_token(self, auth_client_a, user_a):
        resp = auth_client_a.post('/api/boards/', {'title': 'new_board'})
        board = Board.objects.get(id=resp.data['id'])
        assert board.owner == user_a

    def test_list_own_boards(self, auth_client_a, board_a):
        resp = auth_client_a.get('/api/boards/')
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]['id'] == board_a.id


@pytest.mark.django_db
class TestBoardIsolation:
    def test_list_excludes_others_boards(self, auth_client_a, board_a, board_b):
        ''' проверяем что один пользователь не видит доски(проекты) другого пользователя '''
        resp = auth_client_a.get('/api/boards/')
        ids = [b['id'] for b in resp.data]
        assert board_a.id in ids
        assert board_b.id not in ids

    def test_cannot_retrieve_others_board(self, auth_client_a, board_b):
        # прямой доступ к чужой доске отсутствует (404)
        resp = auth_client_a.get('/api/boards/{board_b.id}/')
        assert resp.status_code == 404

    def test_cannot_update_others_board(self, auth_client_a, board_b):
        resp = auth_client_a.patch('/api/boards/{board_b.id}/', {'title': 'changed_title'})
        assert resp.status_code == 404
        board_b.refresh_from_db()
        assert board_b.title != 'changed_title'

    def test_cannot_delete_others_board(self, auth_client_a, board_b):
        resp = auth_client_a.delete('/api/boards/{board_b.id}/')
        assert resp.status_code == 404
        assert Board.objects.filter(id=board_b.id).exists()
    