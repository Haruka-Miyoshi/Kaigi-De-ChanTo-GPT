import sys
sys.path.append('..')

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from linebot import LineBotApi

import os

if not os.path.exists('./data'):
    os.mkdir('./data')

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["TOKEN"]

class Downloader:
    def __init__(self):
        # オーディオファイル端子
        self.audio_filename = '.m4a'
        # 画像ファイル端子
        self.image_filename = '.png'
        # ビデオファイル端子
        self.video_filename = '.mp4'
        # 保存先のファイルパス
        self.file_path = './data'

    # ファイルをダウンロードする処理
    def get_file(self, id, event_type):
        # 実行時の時刻を取得
        now_time = datetime.now().time()
        
        time = now_time.strftime('%H%M%S')
        
        line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

        message_content = line_bot_api.get_message_content(id)

        # 音声データの場合
        if event_type == 'audio':
            file_path = self.file_path + '/audio/' + time + self.audio_filename
            with open(file_path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)
        
        elif event_type == 'video':
            file_path = self.file_path + '/video/' + time + self.video_filename
            with open(file_path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)
            
        return file_path