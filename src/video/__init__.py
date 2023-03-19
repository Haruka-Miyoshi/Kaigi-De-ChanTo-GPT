import sys
sys.path.append('..')

from dotenv import load_dotenv
load_dotenv()

import os
import openai
import ffmpeg
from datetime import datetime

# 動画からテキストへ文字起こし
class VideoToText:
    def __init__(self):
        self.split_time = 5 * 60
        self.output_dir = './data/audio/'

    def get_text(self, file_path):
        # OpenAI API KEY
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        # 入力ファイルの情報を取得
        probe = ffmpeg.probe(file_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        duration = float(video_info['duration'])
        
        # 実行時の時刻を取得
        now_time = datetime.now().time()
        
        time = now_time.strftime('%H%M%S')
        
        text = ""
        # 分割された音声ファイルの抽出
        for t in range(0, int(duration), self.split_time):
            # 分割された音声ファイルのファイル名
            output_file = f'{self.output_dir}/{time}_{t}.mp3'

            # 分割された部分の動画ファイルを作成
            stream = ffmpeg.input(file_path, ss=t, t=self.split_time)

            # 音声ストリームの抽出とエンコード
            audio = stream.audio
            audio = ffmpeg.output(audio, output_file, acodec='libmp3lame')

            # FFmpegを実行する
            ffmpeg.run(audio)

            # OpenAIのWhisperを使って音声から文字起こしする
            audio_file = open(output_file, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

            # 文字起こし結果をためる
            text += transcript.text

        return text