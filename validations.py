from cerberus import Validator

emotion_list = [
    'neutral',
    'happy',
    'sad',
    'angry',
    'fearful',
    'disgusted',
    'surprised'
]

allow_event = [
    'change_emotion',
    'change_setting_emoji',
    'reaction',
    'switch_afk',
    'switch_speaking'
]

websocket_validator = {
    'change_emotion': Validator(
        {
            'event': {
                'type': 'string',
                'allowed': ['change_emotion']
            },
            'emotion': {
                'type': 'string',
                'allowed': emotion_list
            }
        }
    ),
    'change_setting_emoji': Validator(
        {
            'event': {
                'type': 'string',
                'allowed': ['change_setting_emoji']
            },
            'emotion': {
                'type': 'string',
                'allowed': emotion_list
            },
            'emoji': {
                'type': 'integer',
                'min': 0
            }
        }
    ),
    'reaction': Validator(
        {
            'event': {
                'type': 'string',
                'allowed': ['reaction']
            },
            'reaction': {
                'type': 'string'
            },
            'is_animation': {
                'type': 'boolean'
            }
        }
    ),
    'switch_afk': Validator(
        {
            'event': {
                'type': 'string',
                'allowed': ['switch_afk']
            },
            'is_afk': {
                'type': 'boolean'
            }
        }
    ),
    'switch_speaking': Validator(
        {
            'event': {
                'type': 'string',
                'allowed': ['switch_speaking']
            },
            'is_speaking': {
                'type': 'boolean'
            }
        }
    ),
}