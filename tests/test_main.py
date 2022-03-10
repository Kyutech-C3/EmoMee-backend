from datetime import datetime, timedelta
import pytest
from .fixtures import client, use_test_db_fixture, session_for_test, room_for_test
from validations import websocket_request_validator, websocket_responce_validator

def compare_expire_term(str_created_at: str, str_expired_at: str, hour: int = 24) -> bool:
    expired_at = datetime.strptime(str_expired_at, '%Y-%m-%dT%H:%M:%S.%f')
    created_at = datetime.strptime(str_created_at, '%Y-%m-%dT%H:%M:%S.%f')
    return (expired_at - created_at) - timedelta(hours=hour) < timedelta(seconds=1)

@pytest.mark.usefixtures('use_test_db_fixture')
class TestRoom:
    def test_create_room(use_test_db_fixture):
        """
        create room
        """
        res = client.post('/api/v1/room')
        
        assert res.status_code == 200
        res_json = res.json()
        assert compare_expire_term(res_json['created_at'], res_json['expired_at'])
        assert res_json['users'] == []

    def test_create_room_set_limit(use_test_db_fixture):
        """
        create room and set limit
        """
        limit: int = 12
        res = client.post('/api/v1/room', json={
            'limit': limit
        })
        assert res.status_code == 200
        res_json = res.json()
        assert compare_expire_term(res_json['created_at'], res_json['expired_at'], limit)
        assert res_json['users'] == []

    def test_join_room(use_test_db_fixture, room_for_test):
        user_name = 'test_user'
        with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name}") as websocket:
            data = websocket.receive_json()
            assert data['event'] == 'init_info'
            assert websocket_responce_validator[data['event']](data)
            me = data['room']['users'][0]
            assert me['name'] == user_name

    def test_join_other_user(use_test_db_fixture, room_for_test):
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name}") as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name_other}") as _:
                data = websocket.receive_json()
                assert data['event'] == 'join_user'
                assert websocket_responce_validator[data['event']](data)
                new_user = data['user']
                assert new_user['name'] == user_name_other

    def test_exit_other_user(use_test_db_fixture, room_for_test):
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name}") as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name_other}") as _:
                _ = websocket.receive_json()
            data = websocket.receive_json()
            assert data['event'] == 'exit_user'
            assert websocket_responce_validator[data['event']](data)
            exit_user = data['user']
            assert exit_user['name'] == user_name_other

    def test_change_emotion(use_test_db_fixture, room_for_test):
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name}") as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name_other}") as websocket_other:
                join_info = websocket.receive_json()
                other_user_id = join_info['user']['user_id']
                websocket_other.send_json({
                    "event": "change_emotion",
                    "emotion": "happy"
                })
                data = websocket.receive_json()
                assert data['event'] == 'change_emotion'
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id

    def test_join_other_user(use_test_db_fixture, room_for_test):
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name}") as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f"/ws/room/{room_for_test.room_id}?user_name={user_name_other}") as _:
                data = websocket.receive_json()
                assert data['event'] == 'join_user'
                assert websocket_responce_validator[data['event']](data)
                new_user = data['user']
                assert new_user['name'] == user_name_other
