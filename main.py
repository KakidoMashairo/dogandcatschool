import os
import face_detect as f  # face_detect.py
import base64
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# ラベル定義
DOG_LABEL = 0
CAT_LABEL = 1

animal_list = ['犬', '猫']

@app.route("/")
def hello_world():
    return "hello World!"

@app.route("/callback", methods = ['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
# テキストの場合はオウム返し
def handle_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    push_img_id = event.message.id # 投稿された画像IDを取得
    message_content = line_bot_api.get_message_content(push_img_id) # LINEサーバー上に自動保存された画像を取得
    push_img = b""
    for chunk in message_content.iter_content():
        push_img += chunk #画像をiter_contentでpush_imgに順次代入

    push_img = base64.b64encode(push_img) # APIに通すためbase64エンコード
    msg = f.face_detect(push_img)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

if __name__ == "__main__":
   #    app.run()
   port = int(os.getenv("PORT"))
   app.run(host="0.0.0.0", port=port)