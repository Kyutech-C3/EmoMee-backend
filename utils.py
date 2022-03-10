import json
from datetime import datetime
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

def get_guild_and_vc_id(room_id: str) -> Tuple[str, str]:
    discord_info = room_id.split('-')
    guild_id = decimal.Decimal(int(discord_info[0]))
    vc_id = decimal.Decimal(int(discord_info[1]))

    guild_id /= decimal.Decimal(7)
    vc_id /= decimal.Decimal(11)
    
    return str(int(guild_id)), str(int(vc_id))
    
def get_room_id_by_discord_info(guild_id: int, vc_id: int) -> str:
    room_id = f'{guild_id*7}-{vc_id*11}'