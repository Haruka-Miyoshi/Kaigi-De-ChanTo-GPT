from flask import Flask, request, abort
from linebot import ( LineBotApi, WebhookHandler )
from linebot.exceptions import ( InvalidSignatureError )
from linebot.models import ( MessageEvent, AudioMessage, ImageMessage, VideoMessage, TextMessage, TextSendMessage )

from dotenv import load_dotenv
load_dotenv()

import os
from downloader import Downloader
from api import ChatAPI
from speech import SpeechRecognition
from video import VideoToText

# インスタンス
app = Flask(__name__)
dl = Downloader()

CONTEXT_PATH = './content.txt'
# contextファイルを読み込み
f = open(CONTEXT_PATH, 'r', encoding='UTF-8')
# テキストを読み込み
context = f.read()
gpt = ChatAPI(context)

speech_to_text = SpeechRecognition()
video_to_text = VideoToText()

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# コールバック関数
@app.route("/callback", methods=['POST'])
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

# テキストメッセージが送信された場合
@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    # 送信されたメッセージを取得
    text_message = event.message.text
    # chatGPTに投げる
    res = gpt.run(text_message)
    # 送信相手に結果を送る
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=res))

# 音声メッセージが送信された場合
@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    # イベントからIDとイベント種類を取得
    id = event.message.id
    event_type = event.message.type
    # m4aファイルで保存する
    file_path = dl.get_file(id, event_type)
    # 音声認識
    conv_text = speech_to_text.get_text(file_path)

    # chatGPTに投げる
    text_message = gpt.run(conv_text)

    line_bot_api.reply_message(
        event.reply_token, 
        TextSendMessage(text=text_message)
        )

# ビデオメッセージが送信された場合
@handler.add(MessageEvent, message=VideoMessage)
def handle_audio(event):
    # イベントからIDとイベント種類を取得
    id = event.message.id
    event_type = event.message.type
    # ファイルで保存する
    file_path = dl.get_file(id, event_type)

    # 動画から文字起こし
    conv_text = video_to_text.get_text(file_path)

    # chatGPTに投げる
    text_message = gpt.run(conv_text)

    line_bot_api.reply_message(
        event.reply_token, 
        TextSendMessage(text=text_message)
        )

# 実行文
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(debug=False, host='0.0.0.0', port=8000)