from flask import Flask, render_template, request
import socket
import pyaudio
import time
import requests
import json

app = Flask(__name__)

def remove_emoticon(text):
    if ':)' in text:
        index = text.index(':)')
        result = text[:index]
        return result
    else:
        return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    text = request.form['user_input']

    if text == "end":
        return "Goodbye!"

    clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clisock.connect(("localhost", 3123))
    clisock.send(text.encode("utf-8"))
    output = clisock.recv(1024).decode("utf-8")
    output = remove_emoticon(output)
    clisock.close()

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

    return output

if __name__ == '__main__':
    app.run(debug=True)
