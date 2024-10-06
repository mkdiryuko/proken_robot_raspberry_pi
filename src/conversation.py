import os
import subprocess
import asyncio
import aiohttp
import aiofiles
from openai import OpenAI, AsyncOpenAI

# Whisper APIキーの設定
OpenAI.api_key = 'OPENAI_API_KEY'
client = OpenAI()
asyncio_client = AsyncOpenAI()

current_dir = os.path.dirname(os.path.abspath(__file__))
JTALK_FILEPATH = os.path.join(current_dir,"..","audio","jtalk_mei.wav")

# 音声合成ソフトjtalk
def jtalk_mei(t):
    open_jtalk=['open_jtalk']
    mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice']
    speed=['-r','0.8']
    outwav=['-ow',JTALK_FILEPATH]
    cmd=open_jtalk+mech+htsvoice+speed+outwav
    c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    c.stdin.write(t.encode())
    c.stdin.close()
    c.wait()
    aplay = ['aplay','-q',JTALK_FILEPATH]
    wr = subprocess.run(aplay)

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

    except KeyboardInterrupt:
        print("リアルタイム変換を終了します")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    return transcription.text

def create_conversation_text(text):
    prompt = "以下の条件のもとで、会話をしてください。\n条件1:日本語で回答する\n条件2:あなたの名前は[プロケンロボット]\n条件3:1人称はボク\n条件4:語尾に「です」「ます」を使わないでください\n条件5:フレンドリーに\n条件6:一文で完結してください"
    try:
        response = client.chat.completions.create(
            model = "gpt-4-turbo",
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature = 0,
            max_tokens = 100,
            timeout = 30
        )
        res_text = response.choices[0].message.content
    except:
        res_text = "ごめんね、もう一度質問してくれないかな"
    print(res_text)
    return res_text

# jtalk 非同期関数
async def async_jtalk_mei(t):
    open_jtalk = ['open_jtalk']
    mech = ['-x', '/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice = ['-m', '/usr/share/hts-voice/mei/mei_normal.htsvoice']
    speed = ['-r', '0.8']
    outwav = ['-ow', JTALK_FILEPATH]
    cmd = open_jtalk + mech + htsvoice + speed + outwav

    # 非同期で open_jtalk を実行
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE
    )
    
    await process.communicate(t.encode())  # 標準入力に文字列を送信
    await process.wait()  # 処理が終了するまで待機

    # 非同期で aplay を実行
    aplay = ['aplay', '-q', JTALK_FILEPATH]
    await asyncio.create_subprocess_exec(*aplay)

# Whisper API 非同期処理関数
async def transcribe_audio(audiofile_path):
    print("Whisperに音声を送信中...")
    url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {
        'Authorization': f"Bearer {os.environ.get('OPENAI_API_KEY')}",
    }
    
    async with aiofiles.open(audiofile_path, 'rb') as file:
        data = aiohttp.FormData()
        data.add_field(
            "file",
            file,
            filename=audiofile_path.split("/")[-1],
            content_type="audio/wav"
        )
        data.add_field("model", "whisper-1")
        data.add_field("language", "ja")
        data.add_field("response_format", "json")
        data.add_field("temperature", "0.2")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(result['text'])
                    return result['text']
                else:
                    print(f"Error: {response.status}")
                    return None

# ChatGPT API 非同期処理関数
async def chatgpt_query(text):
    print("ChatGPTにテキストを送信中...")
    prompt = "以下の条件のもとで、会話をしてください。\n条件1:日本語で回答する\n条件2:あなたの名前は[プロケンロボット]\n条件3:1人称はボク\n条件4:語尾に「です」「ます」を使わないでください\n条件5:フレンドリーに\n条件6:一文で完結してください"
    try:
        async with aiohttp.ClientSession() as session:
            response = await asyncio_client.chat.completions.create(
                messages=[
                    {"role": "system", "content":prompt},
                    {"role": "user", "content": text}
                ],
                model = "gpt-4-turbo",
                max_tokens = 100,
                timeout = 30
            )
        res_text = response.choices[0].message.content
    except:
        res_text = "もう一度質問してくれるかな？"
    return res_text

async def thinking(text:str):
    try:
        while True:
            await async_jtalk_mei(text)
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        print("考え中タスク終了")

async def thinking_task(audio_data):
    print("考え中...")
    # 考え中...と喋らせるタスクを設定
    thinking_task = asyncio.create_task(thinking("・・・考え中です..."))
    
    transcribed_text = await transcribe_audio(audio_data)
    gpt_response = await chatgpt_query(transcribed_text)

    thinking_task.cancel()

    return gpt_response
