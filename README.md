# EmoMee Backend
## How to Use
1. ルームの作成  
    `/api/v1/room`を叩きルームを作成する
2. ルームへの参加  
    `/ws/room/{room_id}?user_name={name}`にWebSocketを接続する．
    参加時，ユーザーがWebSocketを飛ばした時，退出時に同じルームのユーザーにWebSocketが飛ぶ．

### WebSocketの型
- ウェブソケット接続時
  ```json
  {
    "event": "init_info",
    "room": {
      "room_id": "hogehoge-piyopiyo-fuga",
      "expired_at": "2022-03-09T07:10:45.989Z",
      "created_at": "2022-03-09T07:10:45.989Z",
      "users": [
        {
          "user_id": "hogehoge-fugafuga-1234",
          "name": "hato",
          "emotion": "neutral",
          "emoji": {
            "neutral": 0,
            "happy": 0,
            "sad": 0,
            "angry": 0,
            "fearful": 0,
            "disgusted": 0,
            "surprised": 0
          },
          "is_afk": false,
          "is_speaking": false
        },
        {
          "user_id": "hogehoge-fugafuga-1234",
          "name": "hato",
          "emotion": "neutral",
          "emoji": {
            "neutral": 0,
            "happy": 0,
            "sad": 0,
            "angry": 0,
            "fearful": 0,
            "disgusted": 0,
            "surprised": 0
          },
          "is_afk": false,
          "is_speaking": false
        }
      ]
    },
    "user_id": "hogehoge-fugafuga-1234"
  }
  ```

- 新規ルームメンバー参加時
  ```json
  {
    "event": "join_user", 
    "user": {
      "user_id": "hogehoge-fugafuga-1234",
      "name": "hato",
      "emotion": "neutral",
      "emoji": {
        "neutral": 0,
        "happy": 0,
        "sad": 0,
        "angry": 0,
        "fearful": 0,
        "disgusted": 0,
        "surprised": 0
      },
      "is_afk": false,
      "is_speaking": false
    }
  }
  ```

- ルームメンバー退出時
  ```json
  {
    "event": "exit_user",
    "user": {
      "user_id": "hogehoge-fugafuga-1234",
      "name": "hato",
      "emotion": "neutral",
      "emoji": {
        "neutral": 0,
        "happy": 0,
        "sad": 0,
        "angry": 0,
        "fearful": 0,
        "disgusted": 0,
        "surprised": 0
      },
      "is_afk": false,
      "is_speaking": false
    }
  }
  ```

- 表情の変化時
  - リクエスト
    ```json
    {
        "event": "change_emotion",
        "emotion": "happy"
    }
    ```

  - レスポンス
    ```json
    {
        "event": "change_emotion",
        "emotion": "happy",
        "user_id": "hogehoge-fugafuga-1234"
    }
    ```

- 表情ごとに使用する絵文字の変更時
  - リクエスト
    ```json
    {
        "event": "change_setting_emoji",
        "emotion": "happy",
        "emoji": 2
    }
    ```

  - レスポンス
    ```json
    {
        "event": "change_setting_emoji",
        "emotion": "happy",
        "emoji": 2,
        "user_id": "hogehoge-fugafuga-1234"
    }
    ```

- リアクション時
  - リクエスト
    ```json
    {
        "event": "reaction",
        "reaction": "reaction_name.png",
        "is_animation": false
    }
    ```

  - レスポンス
    ```json
    {
        "event": "reaction",
        "reaction": "reaction_name.png",
        "is_animation": false,
        "user_id": "hogehoge-fugafuga-1234"
    }
    ```

- 離席時
  - リクエスト
    ```json
    {
        "event": "switch_afk",
        "is_afk": true
    }
    ```

  - レスポンス
    ```json
    {
        "event": "switch_afk",
        "is_afk": true,
        "user_id": "hogehoge-fugafuga-1234"
    }
    ```

- 音声認識時
  - リクエスト
    ```json
    {
        "event": "switch_speaking",
        "is_speaking": true
    }
    ```

  - レスポンス
    ```json
    {
        "event": "switch_speaking",
        "is_speaking": true,
        "user_id": "hogehoge-fugafuga-1234"
    }
    ```
