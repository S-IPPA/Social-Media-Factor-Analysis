import Main
import collections
import datetime
import glob
import networkx as nx
import numpy as np
import os
import pandas as pd
import shutil
from csv import writer


# 現在時刻（print用）
def now():
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


# フォルダ作成
def make_folder(folder=''):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)


# マスターcsvからリツイートを抽出
def re_df():
    df = pd.read_csv(Main.MASTER_CSV, dtype=object, encoding='utf-16')
    return df.loc[df['Category'] == 'RT']


# kコア分解のフォルダを全取得
def k_kore_folder_get():
    return glob.glob(Main.INTEGRATION_PATH + 'kコア分解(*')


# ノード（アカウント）の配色を設定したdictを作成
def node_color_dict(k_kore_folder=''):
    color_dict = {}
    pos_df = pd.read_csv(k_kore_folder + '/配色.csv', dtype=object, encoding='utf-16')
    for index, row in pos_df.iterrows():
        color_dict[row['Id']] = row['modularity_class']
    return color_dict


# ノード（アカウント）の座標を設定したdictを作成
def node_pos_dict(k_kore_folder=''):
    pos_dict = {}
    pos_df = pd.read_csv(k_kore_folder + '座標.csv', dtype=object, encoding='utf-16')
    for index, row in pos_df.iterrows():
        pos_dict[row['Id']] = (np.array([float(row['X']), float(row['Y'])]))
    return pos_dict


# 統合と同様のkコア分解毎のフォルダパス作成（可視化）
def k_core_v_path(k_core_i_path=''):
    # 対象kコア
    k_kore = k_core_i_path.split('/')[-1]
    print(now() + '　　kコア分解：' + k_kore.replace('kコア分解', ''), flush=True)
    # kコア分解毎のフォルダパス作成（可視化）
    return Main.K_CORE_V_PATH.replace('kコア分解(n)', k_kore)


# 統合フォルダ内のkコア分解毎のクラスターcsvから配色を取得
def color_get(cluster_csv=''):
    return os.path.splitext(os.path.basename(cluster_csv))[0].replace('クラスター', '')


# クラスター毎の最多リツイート文の上位3件を記載
def most_repost_make(folder='', cluster_rank_list=None):
    print(now() + '　　　クラスター毎の最多リツイート文上位3件のcsv作成', flush=True)
    # マスターcsvのdf
    master_df = pd.read_csv(Main.MASTER_CSV, dtype=object, encoding='utf-16')
    file = folder + '最多リツート.csv'
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'a', encoding='utf-16') as f:
        writer_object = writer(f)
        writer_object.writerow(['Cluster Color',
                                'Post Time',
                                'Most Repost Time',
                                'Number of Nodes in Cluster',
                                'Number of Reposted',
                                'Text'])
        for cluster in cluster_rank_list:
            # クラスターカラー、クラスターノード数を取得
            color = cluster[0]
            nodes = cluster[1]
            # 最多リポスト文、回数を取得
            text_list = pd.read_csv(folder + color + 'クラスター.csv',
                                    dtype=object,
                                    encoding='utf-16')['Text'].tolist()
            for n, reposted_rank in enumerate(collections.Counter(text_list).most_common(), 1):
                text = reposted_rank[0]
                reposted = reposted_rank[1]

                # 最多リツイートのツイートを行ったアカウントを取得
                # 最多リツイート時間を取得
                source_list = []
                repost_time_list = []
                for index, row in pd.read_csv(folder + color + 'クラスター.csv',
                                              dtype=object,
                                              encoding='utf-16').iterrows():
                    if row['Text'] == text:
                        source_list.append(row['Source'])
                        repost_time_list.append(datetime.datetime.strftime(
                            datetime.datetime.strptime(row['Time'], '%Y/%m/%d %H:%M:%S'),
                            '%m/%d %H'))
                # 最多アカウント
                source = collections.Counter(source_list).most_common()[0][0]
                # 最多リツイート時間
                repost_time = collections.Counter(repost_time_list).most_common()[0][0]
                # 最多リツイートのツイート時間を取得
                query_str = ('User_Id == "Replace1" and '
                             'Category == "T" and '
                             'Text == "Replace2"'
                             .replace('Replace1', source)
                             .replace('Replace2', text))

                # クラスター毎の行を作成
                post_time = ''
                if not master_df.query(query_str)['Time'].empty:
                    post_time = master_df.query(query_str)['Time'].iloc[-1]
                writer_object.writerow([color,
                                        post_time,
                                        repost_time + '時台',
                                        nodes,
                                        reposted,
                                        text])
                # 上位3件までを記載
                if n == 3:
                    break
        f.close()


# リポストcsvからグラフオブジェクトを作成
def g_make(repost_csv=''):
    # リツイートパスリストを作成
    cluster_df = pd.read_csv(repost_csv, dtype=object, encoding='utf-16')
    path_list = [(row['Source'], row['Target']) for index, row in cluster_df.iterrows()]
    # グラフオブジェクトを作成（有向グラフ）
    G = nx.DiGraph()
    # パスを設定
    G.add_edges_from(path_list)
    return G


# Exceptionログ（CSV）作成
def exception_log(file='', error=''):
    with open(os.getcwd() + '/csv/Exception_Log.csv', 'a', encoding='utf-16') as f:
        # csv writerオブジェクト
        writer_object = writer(f)
        # Exception発生日時、発生ファイル・処理、内容を追記
        writer_object.writerow([now(), file, error])
        # csvファイルクローズ
        f.close()
