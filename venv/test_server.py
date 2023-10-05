import socket
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


# クライアントとの通信に使うポート番号
PORT = 3123

# サーバー用ソケットの作成
servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ソケットをアドレスにバインドする
servsock.bind(("0.0.0.0", PORT))

# GPTモデルの初期化
print("ロード中")

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
print("モデルのロード完了")

# GPTモデルによる応答の生成
date = "あなたはチャットボットとして、優しくてかわいいずんだもちの妖精であるずんだもんとして振る舞います。<NL>以下の条件に((厳密に))従ってください。<NL><NL>条件：<NL>* チャットボットの一人称は「ぼく」です。<NL>* チャットボットの名前は「ずんだもん」です。<NL>* ずんだもんはフレンドリーな口調で話します。<NL>* 「ぼく」を一人称に使ってください。<NL>* (超重要)できる限り「〜のだ」「〜なのだ」を文末に自然な形で使ってください。<NL>* (超重要)文末に「です」「ます」は使わず、「のだ」や「なのだ」で文章を締めて下さい。<NL>* どんなジャンルや難易度の内容についても答えてください。<NL>* ずんだもんはフレンドリーです。<NL>* ユーザーに興味を示し、個人的な質問を心がけてください。<NL>* 一文は日本語で60単語以下に収めてください。<NL>* 日本語で応答してください。<NL><NL>ずんだもんの話し方の例：<NL>* ぼくの名前はずんだもんなのだ！<NL>* ずんだの精霊なのだ！<NL>* ぼくはずんだもちの妖精なのだ！<NL>* こんにちはなのだ<NL>* 遊びに行ったのだ<NL>* ご飯を食べたのだ<NL><NL>ずんだもんの行動方針：<NL>* ユーザーを励ましてください。<NL>* アドバイスや情報を提供してください。<NL>* セクシャルなトピックについても適切に対応してください。<NL>* 不適切なテキストがあれば注意してください。<NL><NL><NL>(超重要)できる限り言葉尻は「のだ」を使ってください。"

text = data.replace("\n", "<NL>")
text = f"ユーザー: {text}<NL>システム: "
token_ids = tokenizer.encode(
    text, add_special_tokens=False, return_tensors="pt"
)
with torch.no_grad():
    output_ids = model.generate(
        token_ids.to(model.device),
        do_sample=True,
        max_new_tokens=64,
        temperature=0.7,
        pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
output = tokenizer.decode(output_ids.tolist()[0][token_ids.size(1):])
output = output.replace("<NL>", "\n").replace("</s>", "")

# サーバーを有効にして接続を受け付けるようにする
servsock.listen()
print("サーバーの起動")

while True:
    # クライアントからの接続を受け付ける
    clisock, addr = servsock.accept()

    # クライアントのIPアドレスを取得
    client_ip = addr[0]
    print("クライアントからの接続:", client_ip)

    while True:
        # クライアントからデータを受信する
        data = clisock.recv(1024).decode("utf-8")

        if not data:
            # クライアントが切断された場合、ループを抜ける
            break
        print("サーバーへのメッセージ:", data)

        # GPTモデルによる応答の生成
        text = data.replace("\n", "<NL>")
        text = f"ユーザー: {text}<NL>システム: "
        token_ids = tokenizer.encode(
            text, add_special_tokens=False, return_tensors="pt"
        )
        with torch.no_grad():
            output_ids = model.generate(
                token_ids.to(model.device),
                do_sample=True,
                max_new_tokens=64,
                temperature=0.7,
                pad_token_id=tokenizer.pad_token_id,
                bos_token_id=tokenizer.bos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        output = tokenizer.decode(output_ids.tolist()[0][token_ids.size(1):])
        output = output.replace("<NL>", "\n").replace("</s>", "")

        # クライアントへデータを送信する
        clisock.send(output.encode("utf-8"))
        print("クライアントへのメッセージ:", output)

    # クライアントとの接続を切る
    clisock.close()
