import openai
import os

import conversation2

audio_url = "http://172.20.10.3:8080/audio.wav"

# OPENAIのAPI_KEYを設定
openai.api_key = os.getenv("OPENAI_API_KEY")

conversation2.get_audio_stream(audio_url)
conversation2.audio_convert_text(audio_url)