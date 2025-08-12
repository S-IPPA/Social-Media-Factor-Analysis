import Common
import Main
import collections
from csv import writer
import glob
import os
import pandas as pd


# 各クラスター処理
def cluster():
    print(Common.now() + '　各クラスター処理開始', flush=True)

    # マスターcsvからリツイートを抽出
    sub_df = Common.re_df()

    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():
        k_kore = k_kore_folder.split('/')[-1]
        print(Common.now() + '　　kコア分解：' + k_kore.replace('kコア分解', ''), flush=True)

        # ノードファイル
        node_file = k_kore_folder + Main.FIRST_NODES_FILE_PATH
        # ノードファイルが存在する場合のみ実施
        if os.path.exists(node_file):

            # ノード配色csv作成
            print(Common.now() + '　　　ノード配色csv作成', flush=True)
            color_df = pd.read_csv(node_file, dtype=object)
            class_rank_list = (
                collections.Counter(pd.read_csv(node_file,
                                                dtype=object)['modularity_class'].tolist()).most_common())
            for n, cluster_rank in enumerate(class_rank_list, 0):
                color_df = color_df.replace({'modularity_class': {cluster_rank[0]: Main.CLUSTER_COLOR[n]}})
            color_df.to_csv(k_kore_folder + '/配色.csv', encoding='utf-16')

            # ノード割合csv作成
            print(Common.now() + '　　　ノード割合csv作成', flush=True)
            pd.DataFrame([(Main.CLUSTER_COLOR[int(n[0])], n[1]) for n in class_rank_list],
                         columns=['modularity_class',
                                  'Count']).to_csv(k_kore_folder + '/ノード割合.csv', encoding='utf-16')

            # 各色クラスターのリツイートcsv作成
            print(Common.now() + '　　　各色クラスターcsv作成', flush=True)
            for color in Main.CLUSTER_COLOR:
                # 対象色のクラスター内アカウントリストを作成
                color_df = pd.read_csv(k_kore_folder + '/配色.csv', dtype=object, encoding='utf-16')
                account_list = []
                for index, row in color_df.iterrows():
                    if row['modularity_class'] == color:
                        account_list.append(row['Id'])
                # 対象色のクラスター（アカウント）が存在する場合のみcsvを作成
                if len(account_list) > 0:
                    file = k_kore_folder + '/' + color + 'クラスター.csv'
                    if os.path.exists(file):
                        os.remove(file)
                    with open(file, 'a', encoding='utf-16') as f_c:
                        writer_object_c = writer(f_c)
                        writer_object_c.writerow(['Time', 'Source', 'Source_Bot_Score',
                                                  'Target', 'Target_Bot_Score', 'Text', 'Sentimental_Score'])
                        # リツイートを全行読み込み
                        for index, row in sub_df.iterrows():
                            # リツイート先アカウント（始点）
                            to_retweet = row['To_ReTweet']
                            # リツイートアカウント（終点）
                            user_id = row['User_Id']
                            if to_retweet in account_list and user_id in account_list:
                                writer_object_c.writerow([row['Time'], to_retweet,
                                                          row['To_ReTweet_Bot_Score'], user_id,
                                                          row['Bot_Score'], row['Text'],
                                                          row['Sentimental_Score']])
                        f_c.close()
                    # kコア分解内のクラスター毎のフォルダ作成（可視化）
                    Common.make_folder(folder=k_kore_folder.replace('統合', '可視化') + '/' + color)

            # リツイート数（クラスター別）csv作成
            print(Common.now() + '　　　リツイート数（クラスター別）csv作成', flush=True)
            # 各kコア分解フォルダ内のリツイートcsv（クラスター毎）を取得
            cluster_list = []
            for cluster_csv in glob.glob(k_kore_folder + '/*クラスター.csv'):
                # クラスターカラー
                modularity_class = Common.color_get(cluster_csv=cluster_csv)
                # リポスト数
                reposts = len(pd.read_csv(cluster_csv, dtype=object, encoding='utf-16')['Text'].tolist())
                cluster_list.append([modularity_class, reposts])
            # リツイート数DataFrame
            retweet_node_df = pd.DataFrame(cluster_list, columns=['modularity_class', 'reposts'])
            # リツイート数を降順にソート
            retweet_node_df = retweet_node_df.sort_values(by='reposts', ascending=False)
            retweet_node_df.to_csv(k_kore_folder + '/リツイート数（クラスター別）.csv', encoding='utf-16')

            # クラスター毎の最多リツイート文の上位3件を記載
            Common.most_repost_make(folder=k_kore_folder + '/',
                                    cluster_rank_list=collections.Counter(
                                        color_df['modularity_class'].tolist()).most_common())


if __name__ == '__main__':
    cluster()
