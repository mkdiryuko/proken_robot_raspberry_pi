from openai import OpenAI
import os
import sys
from src import conversation, audio_record
import time

def main():
    # ロボットに話しかけた声を録音する
    talkfile_path = audio_record.audio_record()
    print(talkfile_path)

    # 応答を作成する
    talk_text = conversation.audio_convert_text(talkfile_path)
    print(talk_text)
    res_text = conversation.create_conversation_text(talk_text)
    print(res_text)

    # 応答を音声に変換する
    conversation.jtalk_mei(res_text)
    time.sleep(15)

if __name__ == "__main__":
    while True:
        main()

