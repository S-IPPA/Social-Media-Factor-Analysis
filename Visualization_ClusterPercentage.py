import Common
import Visualization
import os
import pandas as pd


# 凡例に割合を追加
def labels_make(count_list=None, labels_list=None):
    percentages = [(value / sum(count_list)) * 100 for value in count_list]
    labels = []
    for value, percentage in zip(labels_list, percentages):
        labels.append(value + ' ' + str(round(percentage, 1)) + '%')
    return labels

# クラスター割合図作成
def cluster_percentage():
    print(Common.now() + '　クラスター割合図作成開始', flush=True)

    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():

        # kコア分解毎のフォルダパス取得（可視化）
        folder = Common.k_core_v_path(k_core_i_path=k_kore_folder)

        # ノード割合
        cluster_percentage_csv = k_kore_folder + '/ノード割合.csv'
        # リツイート割合
        repost_percentage_csv = k_kore_folder + '/リツイート数（クラスター別）.csv'
        if os.path.exists(cluster_percentage_csv) and os.path.exists(repost_percentage_csv):
            k_kore = k_kore_folder.split('/')[-1]
            print(Common.now() + '　　kコア分解：' + k_kore.replace('kコア分解', ''), flush=True)
            # ノード割合
            cluster_percentage_df = pd.read_csv(cluster_percentage_csv, dtype=object, encoding='utf-16')
            # 円グラフを描写
            title = 'Node Ratio'
            title = ''
            count_list = cluster_percentage_df['Count'].astype('int').tolist()
            labels_list = cluster_percentage_df['modularity_class'].tolist()
            labels = labels_make(count_list=count_list,
                                 labels_list=labels_list)
            Visualization.pie_chart_legend_v(title=title,
                                                  x=count_list,
                                                  labels=labels,
                                                  colors=labels_list,
                                                  file=folder + 'ノード割合.png')

            # リツイート割合
            repost_percentage_df = pd.read_csv(repost_percentage_csv, dtype=object, encoding='utf-16')
            # 円グラフを描写
            title = 'Repost Ratio'
            title = ''
            count_list = repost_percentage_df['reposts'].astype('int').tolist()
            labels_list = repost_percentage_df['modularity_class'].tolist()
            labels = labels_make(count_list=count_list,
                                 labels_list=labels_list)
            Visualization.pie_chart_legend_v(title=title,
                                                  x=count_list,
                                                  labels=labels,
                                                  colors=labels_list,
                                                  file=folder + 'リツイート割合.png')


if __name__ == '__main__':
    cluster_percentage()
