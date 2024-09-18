import requests
import wave
from openai import OpenAI
import os

# Whisper APIキーの設定
OpenAI.api_key = 'OPENAI_API_KEY'
client = OpenAI()

audio_file = "/home/proken/workspace/proken_robot/src/output.wav"

def audio_convert_text(audio_path):
    print("音声をテキストに変換中..")

    rate = 16000  # サンプルレート

    try:
        # Whisper APIに音声を送信してテキストに変換
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="ja"
                )
            print("テキスト変換結果：", transcription.text)

            # 一時ファイルを削除
            if os.path.exists(audio_file):
                os.remove(audio_file)

    except KeyboardInterrupt:
        print("リアルタイム変換を終了します")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    return transcription.text

def create_conversation(text):
    prompt = "以下の条件のもとで、会話をしてください。\n条件1:日本語で回答する\n条件2:100文字以内で回答する\n条件3:フレンドリーに"
    response = client.chat.completions.create(
        model = "gpt-4-turbo",
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        temperature = 0
    )
    res_text = response.choices[0].message.content
    print(res_text)

    return res_text

input_text = audio_convert_text(audio_file)
create_conversation(input_text)

