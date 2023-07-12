import os
import uvicorn
import nest_asyncio
from pyngrok import ngrok
from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware

from linebot import ( LineBotApi, WebhookHandler )
from linebot.exceptions import ( InvalidSignatureError )
from linebot.models import ( MessageEvent, AudioMessage, ImageMessage, VideoMessage, TextMessage, TextSendMessage )
from starlette.exceptions import HTTPException

from api import ChatAPI
from video import VideoToText
from downloader import Downloader
from speech import SpeechRecognition

from dotenv import load_dotenv
load_dotenv()

# ライブラリインポート
dl = Downloader()
speech_to_text = SpeechRecognition()
video_to_text = VideoToText()

### プロンプトを読み込み
CONTEXT_PATH = './prompt/content.txt'
prompt = open(CONTEXT_PATH, 'r', encoding='UTF-8')
context = prompt.read()
# ChatGPTインスタンス生成
gpt = ChatAPI(context)

### LINE側の設定
# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

app=FastAPI(title="linebot-sample", description="This is sample of LINE Bot.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def root():
    return {"title": app.title, "description": app.description}

@app.post(
    "/callback",
    summary="LINE Message APIからのコールバックです。",
    description="ユーザーからメッセージが送信された際、LINE Message APIからこちらのメソッドが呼び出されます。",
)
async def callback(request: Request, x_line_signature=Header(None)):

    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), x_line_signature)

    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="InvalidSignatureError")

    return "OK"

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

ngrok_auth_token_key=os.environ['NGORK']
ngrok.set_auth_token(ngrok_auth_token_key)
ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)