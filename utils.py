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
