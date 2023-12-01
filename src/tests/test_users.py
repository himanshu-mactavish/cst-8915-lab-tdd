import json

from src.api.models import User


def test_add_user(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        '/users', data=json.dumps({'username': 'john', 'email': 'john@algonquincollege.com'}), content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert 'john@algonquincollege.com was added!' in data['message']


def test_add_user_invalid_json(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        '/users', data=json.dumps({}),
        content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Input payload validation failed' in data['message']


def test_add_user_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()
    resp = client.post('/users',
                       data=json.dumps({"email": "john@testdriven.io"}),
                       content_type='application/json',
                       )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Input payload validation failed' in data['message']


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()
    client.post(
        '/users', data=json.dumps({'username': 'john', 'email': 'john@algonquincollege.com'}),
        content_type='application/json',
    )
    resp = client.post('/users', data=json.dumps(
        {'username': 'john', 'email': 'john@algonquincollege.com'}), content_type='application/json', )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Sorry. That email already exists.' in data['message']


def test_single_user(test_app, test_database, add_user):
    user = add_user('jeffrey', 'jeffrey@testdriven.io')
    client = test_app.test_client()
    resp = client.get(f'/users/{user.id}')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert 'jeffrey' in data['username']
    assert 'jeffrey@testdriven.io' in data['email']


def test_single_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    resp = client.get('/users/999')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert 'User 999 does not exist' in data['message']


def test_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user('john', 'john@algonquincollege.com')
    add_user('fletcher', 'fletcher@notreal.com')
    client = test_app.test_client()
    resp = client.get('/users')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 2
    assert 'john' in data[0]['username']
    assert 'john@algonquincollege.com' in data[0]['email']
    assert 'fletcher' in data[1]['username']
    assert 'fletcher@notreal.com' in data[1]['email']


def test_update_user(test_app, test_database, add_user):
    client = test_app.test_client()
    # Add a user
    resp = client.post(
        '/users', data=json.dumps({'username': 'alice', 'email': 'alice@tdd.io'}),
        content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201

    # Get the user ID from the response
    user_id = data['id']

    # Update the user
    resp = client.put(
        f'/users/{user_id}', data=json.dumps({'username': 'updated_alice', 'email': 'updated_alice@testdriven.io'}),
        content_type='application/json',
    )
    updated_data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert 'User {user_id} has been updated' in updated_data['message']

    # Check if the user information has been updated
    resp = client.get(f'/users/{user_id}')
    updated_user_data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert 'updated_alice' in updated_user_data['username']
    assert 'updated_alice@testdriven.io' in updated_user_data['email']
