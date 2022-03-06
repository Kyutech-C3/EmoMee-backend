# EmoMee Backend
## How to Use
1. ルームの作成
    `/api/v1/room`を叩きルームを作成する
2. ルームへの参加
    `/ws/room/{room_id}?user_name={name}`にWebSocketを接続する．
    参加時，ユーザーがWebSocketを飛ばした時，退出時に同じルームのユーザーにWebSocketが飛ぶ．

### ユーザーが使用するWebSocketの型
- 表情の変化時
```json
{
    "event": "change_emotion",
    "user_id": "1234-abcdefgh-dddddddd",
    "emotion": "happy"
}
```

- 表情ごとに使用する絵文字の変更時
```json
{
    "event": "change_setting_emoji",
    "user_id": "1234-abcdefgh-dddddddd",
    "emotion": "happy",
    "emoji": ""
}
```

- 離席時
```json
{
    "event": "switch_afk",
    "user_id": "1234-abcdefgh-dddddddd",
    "is_afk": true
}
```
