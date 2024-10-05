from openai import OpenAI
import os
import subprocess

# Whisper APIキーの設定
OpenAI.api_key = 'OPENAI_API_KEY'
client = OpenAI()

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
