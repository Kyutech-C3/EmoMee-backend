import json
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel
import decimal
from typing import Tuple

def class_to_json(obj: BaseModel) -> json:
    return json.loads(json.dumps(obj, default=json_serial))

def json_serial(obj):
    if isinstance(obj, object) and hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def create_dict_with_serial(event_name: str, room_info: dict) -> json:
        return class_to_json({
            'event': event_name,
            'room': room_info
        })

def get_guild_and_vc_id(rid: str) -> Tuple[str, str]:
    hex_gid = rid[:rid.find('-')]
    hex_vcid = rid[rid.find('-')+1:rid.rfind('-')]
    return str(int(hex_gid, 16)), str(int(hex_vcid, 16))
    
def get_room_id_by_discord_info(guild_id: int, vc_id: int) -> str:
    return f'{str(hex(guild_id))[2:]}-{str(hex(vc_id))[2:]}-{str(uuid4())[:4]}'

def generate_user_id(uid) -> str:
    return f'{str(hex(uid))[2:]}-{str(uuid4())[:4]}'