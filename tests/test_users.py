from main import app
from api.services.auth import AuthService


# test get logged-in user
def test_get_user_authorized(mocker, client, mock_user_object):

    app.dependency_overrides[AuthService.get_current_user] = lambda: mock_user_object

    response = client.get('api/v1/users/me')
    
    assert response.json() == mock_user_object
    assert response.status_code == 200


# test get user without login
def test_get_user_unauthorized(mocker, client):

    response = client.get('api/v1/users/me')
    
    assert response.status_code == 401


# test register new user
def test_register(mocker, client, mock_user_object):
    mock_register = mocker.patch('api.services.auth.AuthService.create')

    mock_register.return_value = mock_user_object

    response = client.post('api/v1/users/register', json={
            "email": "testing@demo.com",
            "username": "test",
            "password": "test_password"
        }
    )

    mock_register.assert_called_once()
    assert response.json() == mock_user_object
    assert response.status_code == 201