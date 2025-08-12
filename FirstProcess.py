import Common
import Main
import networkx as nx
import os
import shutil

# ノードファイル名
FIRST_NODES_FILE_NAME = 'First_Analysis_Nodes'
# エッジファイル名
FIRST_EDGES_FILE_NAME = 'First_Analysis_Edges'


# 初期処理
def first_process():
    print(Common.now() + '　初期処理開始', flush=True)

    # マスターcsvからリツイートを抽出
    sub_df = Common.re_df()

    # リツイートを全行読み込み
    retweet_path_tuple_list = []
    for index, row in sub_df.iterrows():
        # リツイートパスタプル（リツイート先アカウント及びリツイートアカウント）を追加
        # 有向グラフはリツイート先アカウント（始点）からリツイートアカウント（終点）
        retweet_path_tuple_list.append((row['To_ReTweet'], row['User_Id']))

    # ノード間のエッジ数（重み）を設定したdictを作成し、最後にリスト化
    print(Common.now() + '　　ノード間のエッジ数（重み）を設定しリスト化', flush=True)
    retweet_path_dict = {}
    for retweet_path_tuple in retweet_path_tuple_list:
        if retweet_path_tuple in retweet_path_dict:
            retweet_path_dict[retweet_path_tuple] += 1
        else:
            retweet_path_dict[retweet_path_tuple] = 1
    retweet_path_list = []
    for retweet_path in retweet_path_dict:
        retweet_path_list.append(retweet_path + (retweet_path_dict[retweet_path],))
    print(Common.now() + '　　　重み設定後パス数：' + str(len(retweet_path_list)), flush=True)

    # グラフオブジェクトにリツイートパスを一括設定
    G = nx.DiGraph()
    G.add_weighted_edges_from(retweet_path_list)
    # 自身へのリツイートのみのエッジは削除（Gコア分解の際のシステムエラー対策）
    G.remove_edges_from(nx.selfloop_edges(G))

    # kコア分解上限数まで繰り返す
    for i in range(Main.K_CORE_MAXIMUM + 1):
        print(Common.now() + '　　kコア分解：' + str(i), flush=True)
        # kコア分解
        G_kore = nx.k_core(G, k=i)
        print(Common.now() + '　　　ノード数：' + str(len(G_kore.nodes)), flush=True)
        print(Common.now() + '　　　エッジ数：' + str(len(G_kore.edges)), flush=True)

        # kコア分解毎のフォルダ作成（統合）
        folder_i = Main.K_CORE_I_PATH.replace('(n)', '(' + str(i) + ')') + 'Gephi/'
        Common.make_folder(folder=folder_i)

        # Gephi用GEXFを作成
        print(Common.now() + '　　　Gephi用GEXF作成', flush=True)
        nx.write_gexf(G_kore, folder_i + 'FirstGephi_kcore-' + str(i) + '.gexf')


if __name__ == '__main__':
    # 統合フォルダ作成
    if os.path.exists(Main.INTEGRATION_PATH):
        shutil.rmtree(Main.INTEGRATION_PATH)
    os.makedirs(Main.INTEGRATION_PATH)
    # 可視化フォルダ作成
    if os.path.exists(Main.VISUALIZATION_PATH):
        shutil.rmtree(Main.VISUALIZATION_PATH)
    os.makedirs(Main.VISUALIZATION_PATH)

    # 初期処理
    first_process()
