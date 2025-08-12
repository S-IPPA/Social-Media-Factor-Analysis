import Common
import Main
import matplotlib
import os
import pandas as pd

import Visualization


# リポスト割合ドーナツグラフ作成（ボット区別あり）
def repost_percentage_bot():
    print(Common.now() + '　リポスト割合ドーナツグラフ作成（ボット区別あり）', flush=True)

    # マスターcsvを読み込み
    df = pd.read_csv(Main.MASTER_CSV, dtype=object, encoding='utf-16')

    # kコア分解前（全体）
    print(Common.now() + '　　kコア分解前（全体）', flush=True)
    # 外側ドーナツグラフ（リポスト、リポスト以外）
    main_list = [0, 0]
    # 内側ドーナツグラフ（リポスト（人間、ボット、不明）、リポスト以外（人間、ボット、不明））
    sub_list = [0, 0, 0, 0, 0, 0]

    # カラーマップから色系統を準備
    a, b = [matplotlib.colormaps['Greens'], matplotlib.colormaps['Blues']]
    main_labels = ['', '']
    main_colors = [a(0.7), b(0.7)]
    sub_labels = ['', '', '', '', '', '']
    sub_colors = [a(0.5), a(0.4), a(0.3), b(0.5), b(0.4), b(0.3)]
    legend = ['1', '2', '3', '4', '5', '6', '7', '8']
    category = ['リポスト',
                'リポスト以外',
                'リポスト（人間）',
                'リポスト（ボット）',
                'リポスト（不明）',
                'リポスト以外（人間）',
                'リポスト以外（ボット）',
                'リポスト以外（不明）']
    bbox_to_anchor = (1, 0.55)

    # ツイートを全行読み込み
    for index, row in df.iterrows():
        # ツイート（リツイート）を行ったアカウントのボットスコア
        bot_score = round(float(row['Bot_Score']), 2)

        # リポストの場合
        if row['Category'] == 'RT':
            # 外側ドーナツグラフのリポスト件数をカウントアップ
            main_list[0] += 1
            # リポストを行ったアカウントの種類を内側ドーナツグラフの件数にカウントアップ
            if bot_score < 0.5:
                sub_list[0] += 1
            elif 0.5 <= bot_score <= 1:
                sub_list[1] += 1
            else:
                sub_list[2] += 1

        # リポスト以外の場合
        else:
            # 外側ドーナツグラフのリポスト以外件数をカウントアップ
            main_list[1] += 1
            # リポスト以外を行ったアカウントの種類を内側ドーナツグラフの件数にカウントアップ
            if bot_score < 0.5:
                sub_list[3] += 1
            elif 0.5 <= bot_score <= 1:
                sub_list[4] += 1
            else:
                sub_list[5] += 1

    # 2重ドーナツグラフを描写
    title = 'Repost Percentage Including Bot'
    title = ''
    Visualization.double_doughnut_v(title=title,
                                         main_list=main_list,
                                         sub_list=sub_list,
                                         main_labels=main_labels,
                                         sub_labels=sub_labels,
                                         main_colors=main_colors,
                                         sub_colors=sub_colors,
                                         legend=legend,
                                         category=category,
                                         bbox_to_anchor=bbox_to_anchor,
                                         file=Main.VISUALIZATION_PATH + 'リポスト割合（ボット含）.png')

    # kコア分解後
    print(Common.now() + '　　kコア分解後', flush=True)
    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():
        # kコア分解毎のフォルダパス取得（可視化）
        folder = Common.k_core_v_path(k_core_i_path=k_kore_folder)

        # 配色csvが存在する場合のみ実施
        if os.path.exists(k_kore_folder + '/配色.csv'):
            # ノード配色dictを作成
            color_dict = Common.node_color_dict(k_kore_folder=k_kore_folder)

            # ドーナツグラフ（人間、ボット、不明）
            main_list = [0, 0, 0]

            # カラーマップから色系統を準備
            main_labels = ['', '', '']
            main_colors = [a(0.5), a(0.4), a(0.3)]
            legend = ['9', '10', '11']
            category = ['リポスト（人間）',
                        'リポスト（ボット）',
                        'リポスト（不明）']
            bbox_to_anchor = (0.85, 0.9)

            # ツイートを全行読み込み
            for index, row in df.iterrows():

                # リツイートアカウント、リツイート先アカウントが共にクラスターに所属する場合
                if row['User_Id'] in color_dict.keys() and row['To_ReTweet'] in color_dict.keys():

                    # ツイート（リツイート）を行ったアカウントのボットスコア
                    bot_score = round(float(row['Bot_Score']), 2)

                    # リポストを行ったアカウントの種類を内側ドーナツグラフの件数にカウントアップ
                    if bot_score < 0.5:
                        main_list[0] += 1
                    elif 0.5 <= bot_score <= 1:
                        main_list[1] += 1
                    else:
                        main_list[2] += 1

            # ドーナツグラフを描写
            title = 'Repost Percentage Including Bot' + k_kore_folder.split('/')[-1]
            title = ''
            Visualization.single_doughnut_v(title=title,
                                                 main_list=main_list,
                                                 main_labels=main_labels,
                                                 main_colors=main_colors,
                                                 legend=legend,
                                                 category=category,
                                                 bbox_to_anchor=bbox_to_anchor,
                                                 file=folder + 'リポスト割合（ボット含）.png')


if __name__ == '__main__':
    repost_percentage_bot()
