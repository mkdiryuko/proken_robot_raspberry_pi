import pyaudio
import wave
import os

def audio_record():
    # 録音の設定
    FORMAT = pyaudio.paInt16  # 16-bit resolution
    CHANNELS = 1  # モノラル
    RATE = 44100  # サンプリングレート（44.1kHz）
    CHUNK = 1024  # フレームサイズ
    RECORD_SECONDS = 5  # 録音する時間（秒）

    current_dir = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_FILEPATH = os.path.join(current_dir,"..","audio","talk.wav") # talk.wavをauidoディレクトリに保存

    # PyAudioオブジェクトの作成
    audio = pyaudio.PyAudio()

    # 録音開始
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("録音中...")

    frames = []

    # 録音データをフレーム単位で収集
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("録音終了")

    # 録音ストリームの終了とクローズ
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # WAVファイルとして保存
    wavefile = wave.open(OUTPUT_FILEPATH, 'wb')
    wavefile.setnchannels(CHANNELS)
    wavefile.setsampwidth(audio.get_sample_size(FORMAT))
    wavefile.setframerate(RATE)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    return OUTPUT_FILEPATH
