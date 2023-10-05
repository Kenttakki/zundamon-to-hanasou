import requests
import json
import pyaudio
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# 初期化
tokenizer = AutoTokenizer.from_pretrained(
    "rinna/japanese-gpt-neox-3.6b-instruction-ppo",
    use_fast=False,
    torch_dtype=torch.float16,
)
model = AutoModelForCausalLM.from_pretrained(
    "rinna/japanese-gpt-neox-3.6b-instruction-ppo",
    device_map={"": 0},
    load_in_4bit=True
)

while True:
    text = input("入力どうぞ : ")
    if text == "end":
        break
    else:
        text = text.replace("\n", "<NL>")
        text = f"ユーザー: {text}<NL>システム: "
        token_ids = tokenizer.encode(
            text, add_special_tokens=False, return_tensors="pt"
        )
        with torch.no_grad():
            output_ids = model.generate(
                token_ids.to(model.device),
                do_sample=True,
                max_new_tokens=128,
                temperature=0.7,
                pad_token_id=tokenizer.pad_token_id,
                bos_token_id=tokenizer.bos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        output = tokenizer.decode(output_ids.tolist()[0][token_ids.size(1):])
        output = output.replace("<NL>", "\n").replace("</s>", "")
        print(output)

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
