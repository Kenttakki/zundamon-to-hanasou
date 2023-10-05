
from transformers import AutoTokenizer, AutoModelForCausalLM

import torch

tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt-neox-3.6b-instruction-ppo", use_fast=False)
model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt-neox-3.6b-instruction-ppo")

if torch.cuda.is_available():
    model = model.to("cuda")

while True:
    text = input("入力どうぞ : ")
    if text == "end":
        exit()
    else:
        text = text.replace("\n", "<NL>")
        text = f"ユーザー: {text}<NL>システム: "
        token_ids = tokenizer.encode(
            text, add_special_tokens=False, return_tensors="pt"
        )
        with torch.no_grad():
            output_ids = model.generate(
                token_ids.to(model.device),
                max_new_tokens=512,
                do_sample=True,
                temperature=1.0,
                top_p=0.85,
                pad_token_id=tokenizer.pad_token_id,
                bos_token_id=tokenizer.bos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        output = tokenizer.decode(output_ids.tolist()[0][token_ids.size(1) :])
        output = output.replace("<NL>", "\n").replace("</s>", "")
        print(output)

        import requests  # APIを使う
        import json  # APIで取得するJSONデータを処理する
        import pyaudio  # wavファイルを再生する
        import time  # タイムラグをつける


        # 音声合成クエリの作成
        res1 = requests.post('http://127.0.0.1:50021/audio_query', params={'text': output, 'speaker': 1})
        # 音声合成データの作成
        res2 = requests.post('http://127.0.0.1:50021/synthesis', params={'speaker': 1}, data=json.dumps(res1.json()))
        #
        data = res2.content

        # PyAudioのインスタンスを生成
        p = pyaudio.PyAudio()

        # ストリームを開く
        stream = p.open(format=pyaudio.paInt16,  # 16ビット整数で表されるWAVデータ
                        channels=1,  # モノラル
                        rate=24000,  # サンプリングレート
                        output=True)

        # 再生を少し遅らせる（開始時ノイズが入るため）
        time.sleep(0.2)  # 0.2秒遅らせる

        # WAV データを直接再生する
        stream.write(data)

        # ストリームを閉じる
        stream.stop_stream()
        stream.close()

        # PyAudio のインスタンスを終了する
        p.terminate()