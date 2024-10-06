import asyncio
import aiohttp
import os
from openai import AsyncOpenAI
from audio_record import *
from conversation import *

def main():
    # 1.録音
    audio_data = audio_record()
    # イベントループの作成
    loop = asyncio.get_event_loop()
    # 2.WhisperとChatGPTのAPIに投げている間、考え中と喋らせる
    gpt_response = loop.run_until_complete(thinking_task(audio_data))
    # 3.ChatGPTによって作成された回答を喋らせる
    jtalk_mei(gpt_response)

if __name__ == "__main__":
    main()