import Common
import Main
import networkx as nx
import os
import pandas as pd
import webcolors


# Gephi用GEXF作成
def gephi():
    print(Common.now() + '　Gephi用GEXF作成開始', flush=True)
    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():
        # ノードファイル名
        node_file = k_kore_folder + '/配色.csv'
        # エッジファイル名
        edge_file = k_kore_folder + Main.FIRST_EDGES_FILE_PATH

        # ノードファイルとエッジファイルが存在する場合のみ実施
        if os.path.exists(node_file) and os.path.exists(edge_file):
            k_kore = k_kore_folder.split('/')[-1]
            print(Common.now() + '　　kコア分解：' + k_kore.replace('kコア分解', ''), flush=True)

            # ノード配色dictを作成
            color_dict = Common.node_color_dict(k_kore_folder=k_kore_folder)

            # エッジファイルを取得
            edge_df = pd.read_csv(edge_file, dtype=object)
            # リツイートパスタプル（リツイート先アカウント、リツイートアカウント、重み）を追加
            # 有向グラフはリツイート先アカウント（始点）からリツイートアカウント（終点）
            retweet_path_list = [(row['Source'], row['Target'], row['Weight']) for index, row in edge_df.iterrows()]

            # グラフオブジェクトにリツイートパスを一括設定
            G = nx.DiGraph()
            G.add_weighted_edges_from(retweet_path_list)

            # Gephi用GEXFを作成
            file = k_kore_folder + '/Gephi.gexf'
            if os.path.exists(file):
                os.remove(file)
            with open(file, 'a') as f_g:
                for g in G.nodes():
                    # ノード色のRGB色を取得
                    rgb = webcolors.name_to_rgb(color_dict[g])
                    # ノードの配色、座標を設定
                    G.nodes[g]['viz'] = {'color': {'r': rgb.red, 'g': rgb.green, 'b': rgb.blue, 'a': 1}}
                f_g.write(''.join(nx.generate_gexf(G)))
                f_g.close()


if __name__ == '__main__':
    gephi()
