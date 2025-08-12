import Common
import Visualization
import glob
import pandas as pd


# クラスター感情スコア箱ひげ図作成
def cluster_sentimental():
    print(Common.now() + '　クラスター感情スコア箱ひげ図作成', flush=True)

    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():
        # kコア分解毎のフォルダパス取得（可視化）
        folder = Common.k_core_v_path(k_core_i_path=k_kore_folder)

        # クラスター毎のcsvファイルが存在する場合のみ実行
        if len(glob.glob(k_kore_folder + '/*クラスター.csv')) > 0:
            # クラスターリストを作成（ノード数で降順）
            cluster_list = list(dict.fromkeys(pd.read_csv(k_kore_folder + '/最多リツート.csv',
                                                          dtype=object,
                                                          encoding='utf-16')['Cluster Color'].tolist()))
            # ラベルリスト
            label_list = []
            # データリスト
            data_list = []

            for cluster in cluster_list:
                label_list.append(cluster)
                # クラスター毎のcsvを読み込み
                df = pd.read_csv(k_kore_folder + '/' + cluster + 'クラスター.csv', dtype=object, encoding='utf-16')
                data_list.append([round(float(item), 2) for item in df['Sentimental_Score'].tolist()])

            # 水平線
            axhline = True
            axhline_score = 0
            # 箱ヒゲ図の描画
            title = 'Sentimental Score'
            title = ''
            Visualization.box_plot_v(title=title,
                                          x=data_list,
                                          label_list=label_list,
                                          color_list=label_list,
                                          xlabel='Community',
                                          ylabel='Emotional Score',
                                          axhline=axhline,
                                          axhline_score=axhline_score,
                                          file=folder + 'クラスター感情スコア箱ヒゲ図.png')


if __name__ == '__main__':
    cluster_sentimental()
