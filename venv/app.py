# app.py

from flask import Flask, render_template, request
import socket
import pyaudio
import time
import requests
import json

app = Flask(__name__)

# $B%5!<%P!<$N(BIP$B%"%I%l%9$H%]!<%HHV9f(B
SERVER_IP = "localhost"
SERVER_PORT = 3123

# $B%/%i%$%"%s%HMQ$N%=%1%C%H$r:n@.(B
clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clisock.connect((SERVER_IP, SERVER_PORT))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']

    if text == "end":
        clisock.close()
        return "$B=*N;$7$^$7$?!#(B"

    clisock.send(text.encode("utf-8"))

    output = clisock.recv(1024).decode("utf-8")

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

    return output  # $B%5!<%P!<$+$i$N1~Ez$O%F%-%9%H$H$7$FJV$9(B



if __name__ == '__main__':
    app.run(debug=True)
