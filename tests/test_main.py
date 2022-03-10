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
        '''
        create room
        '''
        res = client.post('/api/v1/room')
        
        assert res.status_code == 200
        res_json = res.json()
        assert compare_expire_term(res_json['created_at'], res_json['expired_at'])
        assert res_json['users'] == []

    def test_create_room_set_limit(use_test_db_fixture):
        '''
        create room and set limit
        '''
        limit: int = 12
        res = client.post('/api/v1/room', json={
            'limit': limit
        })
        assert res.status_code == 200
        res_json = res.json()
        assert compare_expire_term(res_json['created_at'], res_json['expired_at'], limit)
        assert res_json['users'] == []

    def test_join_room(use_test_db_fixture, room_for_test):
        '''
        connect websocket and join room
        '''
        user_name = 'test_user'
        event = 'init_info'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            data = websocket.receive_json()
            assert data['event'] == event
            assert websocket_responce_validator[data['event']](data)
            me = data['room']['users'][0]
            assert me['name'] == user_name

    def test_join_other_user(use_test_db_fixture, room_for_test):
        '''
        get join user info
        '''
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        event = 'join_user'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name_other}') as _:
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                new_user = data['user']
                assert new_user['name'] == user_name_other

    def test_exit_other_user(use_test_db_fixture, room_for_test):
        '''
        get exit user info
        '''
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        event = 'exit_user'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name_other}') as _:
                _ = websocket.receive_json()
            data = websocket.receive_json()
            assert data['event'] == event
            assert websocket_responce_validator[data['event']](data)
            exit_user = data['user']
            assert exit_user['name'] == user_name_other

    def test_change_emotion(use_test_db_fixture, room_for_test):
        '''
        send change emotion
        '''
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        emotion = 'happy'
        event = 'change_emotion'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name_other}') as websocket_other:
                join_info = websocket.receive_json()
                other_user_id = join_info['user']['user_id']
                websocket_other.send_json({
                    'event': event,
                    'emotion': emotion
                })
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id
                assert data['emotion'] == emotion

    def test_set_emoji(use_test_db_fixture, room_for_test):
        '''
        change setting emoji
        '''
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        emotion = 'sad'
        emoji_num = 3
        event = 'change_setting_emoji'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name_other}') as websocket_other:
                join_info = websocket.receive_json()
                other_user_id = join_info['user']['user_id']
                websocket_other.send_json({
                    'event': event,
                    'emotion': emotion,
                    'emoji': emoji_num
                })
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id
                assert data['emotion'] == emotion
                assert data['emoji'] == emoji_num

    def test_switch_afk(use_test_db_fixture, room_for_test):
        '''
        switch afk
        '''
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        event = 'switch_afk'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name_other}') as websocket_other:
                join_info = websocket.receive_json()
                other_user_id = join_info['user']['user_id']
                websocket_other.send_json({
                    'event': event,
                    'is_afk': True
                })
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id
                assert data['is_afk'] == True

                websocket_other.send_json({
                    'event': event,
                    'is_afk': False
                })
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id
                assert data['is_afk'] == False

    def test_switch_speaking(use_test_db_fixture, room_for_test):
        '''
        switch speaking
        '''
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        event = 'switch_speaking'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name_other}') as websocket_other:
                join_info = websocket.receive_json()
                other_user_id = join_info['user']['user_id']
                websocket_other.send_json({
                    'event': event,
                    'is_speaking': True
                })
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id
                assert data['is_speaking'] == True

                websocket_other.send_json({
                    'event': event,
                    'is_speaking': False
                })
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id
                assert data['is_speaking'] == False

    def test_send_reaction(use_test_db_fixture, room_for_test):
        '''
        send reaction
        '''
        user_name = 'test_user'
        user_name_other = 'test_user_2'
        event = 'reaction'
        reaction_file_name = 'hoge.png'
        with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name}') as websocket:
            _ = websocket.receive_json()
            with client.websocket_connect(f'/ws/room/{room_for_test.room_id}?user_name={user_name_other}') as websocket_other:
                join_info = websocket.receive_json()
                other_user_id = join_info['user']['user_id']
                websocket_other.send_json({
                    'event': event,
                    'reaction': reaction_file_name,
                    'is_animation': False,
                    'wait_seconds': 1
                })
                data = websocket.receive_json()
                assert data['event'] == event
                assert websocket_responce_validator[data['event']](data)
                assert data['user_id'] == other_user_id
                assert data['reaction'] == reaction_file_name
                assert data['is_animation'] == False
                finish_data = websocket.receive_json()
                assert finish_data['event'] == 'finish_reaction'
                assert websocket_responce_validator[finish_data['event']](finish_data)
                assert finish_data['user_id'] == other_user_id
                assert finish_data['reaction'] == reaction_file_name
                assert finish_data['is_animation'] == False
