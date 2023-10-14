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
