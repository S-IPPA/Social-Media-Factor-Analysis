import Common
import Visualization
import numpy as np
import os
import pandas as pd


# クラスター相関関係ヒートマップ作成
def cluster_relationship():
    print(Common.now() + '　ヒートマップ作成開始', flush=True)

    # マスターcsvからリツイートを抽出
    sub_df = Common.re_df()

    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():
        # kコア分解毎のフォルダパス取得（可視化）
        folder = Common.k_core_v_path(k_core_i_path=k_kore_folder)

        # 配色csvが存在する場合のみ実施
        if os.path.exists(k_kore_folder + '/配色.csv'):

            # ノード配色dictを作成
            color_dict = Common.node_color_dict(k_kore_folder=k_kore_folder)

            # クラスターリストを作成（ノード数で降順）
            cluster_list = list(dict.fromkeys(pd.read_csv(k_kore_folder + '/最多リツート.csv',
                                                          dtype=object,
                                                          encoding='utf-16')['Cluster Color'].tolist()))

            # ヒートマップ用DataFrameを定義
            cluster_count = len(cluster_list)
            hm_df = pd.DataFrame(np.asarray(np.zeros([cluster_count, cluster_count]), dtype=int))
            hm_df = hm_df.sort_index(ascending=False)

            # リツイートを全行読み込み
            for index, row in sub_df.iterrows():
                # リツイートアカウントカラーをX軸、リツイート先アカウントカラーをY軸に設定
                if row['User_Id'] in color_dict.keys() and row['To_ReTweet'] in color_dict.keys():
                    hm_df.loc[
                        cluster_list.index(color_dict[row['User_Id']]),
                        cluster_list.index(color_dict[row['To_ReTweet']])
                    ] += 1

            # ヒートマップ用DataFrameのラベルをクラスター色に変更
            for cluster in cluster_list:
                hm_df = hm_df.rename(columns={cluster_list.index(cluster): cluster},
                                     index={cluster_list.index(cluster): cluster})

            # csvにて保存
            file = folder + 'クラスター相関.csv'
            if os.path.exists(file):
                os.remove(file)
            hm_df.to_csv(file)
            # ヒートマップを描写
            title = folder.split('/')[-2].replace('kコア分解(', 'k-Core Decomposition:').replace(')', '')
            title = ''
            Visualization.heatmap_v(title=title,
                                         df=hm_df,
                                         bar={'label': 'Repost'},
                                         x_label='Repost',
                                         y_label='Reposted',
                                         file=folder + 'クラスター相関.png')


if __name__ == '__main__':
    cluster_relationship()
