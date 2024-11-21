from main import app
from api.services.auth import AuthService

def test_post_task_authorized(mocker, client, mock_task_object, mock_user_object):
    mock_create = mocker.patch('api.services.task.TaskService.create')
    mock_create.return_value = mock_task_object

    app.dependency_overrides[AuthService.get_current_user] = lambda: mock_user_object

    response = client.post('api/v1/tasks', json={
            "title": "Test Task",
            "description": "Test Task Description",
            "dueDate": "2021-09-01",
            "status": "pending",
            "priority": "low",
            "tags": ["test", "task"]
        }
    )

    mock_create.assert_called_once()
    assert response.status_code == 201


def test_post_task_unauthorized(mocker, client, mock_task_object, mock_user_object):
    mock_create = mocker.patch('api.services.task.TaskService.create')
    mock_create.return_value = mock_task_object

    response = client.post('api/v1/tasks', json={
            "title": "Test Task",
            "description": "Test Task Description",
            "dueDate": "2021-09-01",
            "status": "pending",
            "priority": "low",
            "tags": ["test", "task"]
        }
    )

    assert response.status_code == 401


# test update task
def test_update_task_authorized(mocker, client, mock_task_object, mock_user_object):
    mock_update = mocker.patch('api.services.task.TaskService.update')
    mock_update.return_value = mock_task_object

    app.dependency_overrides[AuthService.get_current_user] = lambda: mock_user_object

    new_task = {
            "title": "Test Task",
            "description": "Test Task Description",
            "dueDate": "2021-09-01",
            "status": "pending",
            "priority": "low",
            "tags": ["test", "task"]
        }

    response = client.put('api/v1/tasks/1', json=new_task)

    mock_update.assert_called_once()
    assert response.status_code == 200


# test delete task
def test_delete_task_authorized(mocker, client, mock_task_object, mock_user_object):
    mock_delete = mocker.patch('api.services.task.TaskService.delete')
    mock_delete.return_value = mock_task_object

    app.dependency_overrides[AuthService.get_current_user] = lambda: mock_user_object

    response = client.delete('api/v1/tasks/1')

    mock_delete.assert_called_once()
    assert response.status_code == 200
    assert response.json() == {
        "message": "Task deleted successfully."
    }
