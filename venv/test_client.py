import socket
import pyaudio
import time
import requests
import json

# サーバーのIPアドレスとポート番号
SERVER_IP = "localhost"
SERVER_PORT = 3123

# クライアント用のソケットを作成
clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ソケットをアドレスに接続する
clisock.connect((SERVER_IP, SERVER_PORT))

while True:
    # ユーザーからの入力を取得
    text = input("入力どうぞ: ")
    if text == "end":
        break

    # サーバーにデータを送信する
    clisock.send(text.encode("utf-8"))

    # サーバーからのデータを受信する
    output = clisock.recv(1024).decode("utf-8")
    print("サーバーからの応答:", output)

    # 音声合成と再生
    # 音声合成と再生
    res1 = requests.post('http://127.0.0.1:50021/audio_query', params={'text': output, 'speaker': 1})
    res2 = requests.post('http://127.0.0.1:50021/synthesis', params={'speaker': 1}, data=json.dumps(res1.json()))
    data = res2.content

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
    time.sleep(0.2)
    stream.write(data)
    stream.stop_stream()
    stream.close()
    p.terminate()

# クライアントソケットを閉じる
clisock.close()
