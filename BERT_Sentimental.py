import Main
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as ft
import pandas as pd


# BERTを用いた感情分析
def bert_sentimental():

    # モデルとトークナイザーの準備
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name)

    # GPUが利用可能か確認
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model.to(device)

    # マスターcsvに感情スコアの列を追加
    df = pd.read_csv(Main.MASTER_CSV, dtype=object, encoding='utf-16')
    df.insert(16, 'Emotional Score', 0)

    # マスターcsvを全行読み込み
    i = 0
    for index, row in df.iterrows():
        i += 1
        print(i)

        # 文章をトークン化してテンソルに変換
        inputs = tokenizer(row['Text'], return_tensors="pt", padding=True, truncation=True).to(device)
        # モデルに入力を与えて出力を得る
        with torch.no_grad():
            outputs = model(**inputs)

        # 出力のロジットを取得し、ソフトマックスを適用して確率を計算
        probabilities = ft.softmax(outputs.logits, dim=-1)

        # スコアを計算（-1: ネガティブ、1: ポジティブ）
        # モデルは1～5のラベルで出力されるため、それを-1～1に変換
        score = torch.dot(probabilities.squeeze(), torch.tensor([-1, -0.5, 0, 0.5, 1]).to(device)).item()

        # マスターに感情スコアを追加
        df.loc[df['Tweet_Id'] == row['Tweet_Id'], ['Emotional Score']] = score

    df.to_csv(Main.MASTER_CSV, encoding='utf-16')


if __name__ == '__main__':
    bert_sentimental()
