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

websocket_request_validator = {
    'change_emotion': Validator({
        'event': {
            'type': 'string',
            'allowed': ['change_emotion']
        },
        'emotion': {
            'type': 'string',
            'allowed': emotion_list
        }
    }),
    'change_setting_emoji': Validator({
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
    }),
    'reaction': Validator({
        'event': {
            'type': 'string',
            'allowed': ['reaction']
        },
        'reaction': {
            'type': 'string'
        },
        'is_animation': {
            'type': 'boolean'
        },
        'wait_seconds': {
            'type': 'integer'
        }
    }),
    'switch_afk': Validator({
        'event': {
            'type': 'string',
            'allowed': ['switch_afk']
        },
        'is_afk': {
            'type': 'boolean'
        }
    }),
    'switch_speaking': Validator({
        'event': {
            'type': 'string',
            'allowed': ['switch_speaking']
        },
        'is_speaking': {
            'type': 'boolean'
        }
    })
}

user_validate = {
    'user_id': {
        'type': 'string'
    },
    'name': {
        'type': 'string'
    },
    'emotion': {
        'type': 'string',
        'allowed': emotion_list
    },
    'emoji': {
        'type': 'dict',
        'schema': {
            "neutral": {
                'type': 'integer'
            },
            "happy": {
                'type': 'integer'
            },
            "sad": {
                'type': 'integer'
            },
            "angry": {
                'type': 'integer'
            },
            "fearful": {
                'type': 'integer'
            },
            "disgusted": {
                'type': 'integer'
            },
            "surprised": {
                'type': 'integer'
            }
        }
    },
    'is_afk': {
        'type': 'boolean'
    },
    'is_speaking': {
        'type': 'boolean'
    }
}

websocket_responce_validator = {
    'init_info': Validator({
        'event': {
            'type': 'string',
            'allowed': ['init_info']
        },
        'room': {
            'type': 'dict',
            'schema': {
                'room_id': {
                    'type': 'string'
                },
                'expired_at': {
                    'type': 'string'
                },
                'created_at': {
                    'type': 'string'
                },
                'users': {
                    'type': 'list',
                    'schema': {
                        'type': 'dict',
                        'schema': user_validate
                    }
                }
            }
        },
        'user_id': {
            'type': 'string'
        }
    }),
    'join_user': Validator({
        'event': {
            'type': 'string',
            'allowed': ['join_user']
        },
        'user': {
            'type': 'dict',
            'schema': user_validate
        }
    }),
    'exit_user': Validator({
        'event': {
            'type': 'string',
            'allowed': ['exit_user']
        },
        'user': {
            'type': 'dict',
            'schema': user_validate
        }
    }),
    'change_emotion': Validator({
        'event': {
            'type': 'string',
            'allowed': ['change_emotion']
        },
        'user_id': {
            'type': 'string'
        },
        'emotion': {
            'type': 'string',
            'allowed': emotion_list
        }
    }),
    'change_setting_emoji': Validator({
        'event': {
            'type': 'string',
            'allowed': ['change_setting_emoji']
        },
        'user_id': {
            'type': 'string'
        },
        'emotion': {
            'type': 'string',
            'allowed': emotion_list
        },
        'emoji': {
            'type': 'integer',
            'min': 0
        }
    }),
    'reaction': Validator({
        'event': {
            'type': 'string',
            'allowed': ['reaction']
        },
        'user_id': {
            'type': 'string'
        },
        'reaction': {
            'type': 'string'
        },
        'is_animation': {
            'type': 'boolean'
        }
    }),
    'finish_reaction': Validator({
        'event': {
            'type': 'string',
            'allowed': ['finish_reaction']
        },
        'user_id': {
            'type': 'string'
        },
        'reaction': {
            'type': 'string'
        },
        'is_animation': {
            'type': 'boolean'
        }
    }),
    'switch_afk': Validator({
        'event': {
            'type': 'string',
            'allowed': ['switch_afk']
        },
        'user_id': {
            'type': 'string'
        },
        'is_afk': {
            'type': 'boolean'
        }
    }),
    'switch_speaking': Validator({
        'event': {
            'type': 'string',
            'allowed': ['switch_speaking']
        },
        'user_id': {
            'type': 'string'
        },
        'is_speaking': {
            'type': 'boolean'
        }
    })
}
