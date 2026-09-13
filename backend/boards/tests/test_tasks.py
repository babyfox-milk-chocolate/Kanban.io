import pytest
from boards.models import Task


@pytest.mark.django_db
class TestTaskCRUD:
    def test_create_task_in_own_board(self, auth_client_a, board_a):
        resp = auth_client_a.post("/api/tasks/", {
            "board": board_a.id,
            "title": "New task",
        })
        assert resp.status_code == 201
        assert resp.data["status"] == "todo"  # статус по умолчанию

    def test_list_own_tasks(self, auth_client_a, task_a):
        resp = auth_client_a.get("/api/tasks/")
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_filter_by_board(self, auth_client_a, board_a, task_a):
        resp = auth_client_a.get(f"/api/tasks/?board={board_a.id}")
        assert resp.status_code == 200
        assert all(t["board"] == board_a.id for t in resp.data)

    def test_update_task_status(self, auth_client_a, task_a):
        resp = auth_client_a.patch(f"/api/tasks/{task_a.id}/", {"status": "done"})
        assert resp.status_code == 200
        assert resp.data["status"] == "done"


@pytest.mark.django_db
class TestTaskIsolation:
    """Задачи защищены через связь board__owner."""

    def test_list_excludes_others_tasks(self, auth_client_a, task_a, task_b):
        resp = auth_client_a.get("/api/tasks/")
        ids = [t["id"] for t in resp.data]
        assert task_a.id in ids
        assert task_b.id not in ids

    def test_cannot_retrieve_others_task(self, auth_client_a, task_b):
        resp = auth_client_a.get(f"/api/tasks/{task_b.id}/")
        assert resp.status_code == 404

    def test_cannot_delete_others_task(self, auth_client_a, task_b):
        resp = auth_client_a.delete(f"/api/tasks/{task_b.id}/")
        assert resp.status_code == 404
        assert Task.objects.filter(id=task_b.id).exists()

    def test_cannot_create_task_in_others_board(self, auth_client_a, board_b):
        # пробуем создать задачу в чужой доске 
        resp = auth_client_a.post("/api/tasks/", {
            "board": board_b.id,
            "title": "Unexpected task",
        })
        assert resp.status_code == 403
        assert not Task.objects.filter(title="Unexpected task").exists()