import json
from datetime import datetime
from pydantic import BaseModel

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
