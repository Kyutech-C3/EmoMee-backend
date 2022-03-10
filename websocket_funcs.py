clients = {}
user_list = {}

def func_change_emotion(room_id: str, user_id: str, socket: dict):
    user_list[room_id][user_id]['emotion'] = socket.get('emotion')

def func_change_setting_emoji(room_id: str, user_id: str, socket: dict):
    emotion = socket.get('emotion')
    user_list[room_id][user_id]['emoji'][emotion] = socket.get('emoji')

def func_reaction(room_id: str, user_id: str, socket: dict):
    pass

def func_switch_afk(room_id: str, user_id: str, socket: dict):
    user_list[room_id][user_id]['is_afk'] = socket.get('is_afk')

def func_switch_speaking(room_id: str, user_id: str, socket: dict):
    user_list[room_id][user_id]['is_speaking'] = socket.get('is_speaking')

websocket_funcs = {
    'change_emotion': func_change_emotion,
    'change_setting_emoji': func_change_setting_emoji,
    'reaction': func_reaction,
    'switch_afk': func_switch_afk,
    'switch_speaking': func_switch_speaking
}
