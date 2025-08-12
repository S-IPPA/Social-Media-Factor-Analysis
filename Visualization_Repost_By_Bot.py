from csv import writer
import Common
import Visualization
import glob
import os
import pandas as pd


# ボットによるリポスト件数・割合棒グラフ作成（件数はcsvのみ）
def repost_by_bot():
    print(Common.now() + '　ボットによるリポスト件数・割合棒グラフ作成（件数はcsvのみ）', flush=True)

    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():
        # kコア分解毎のフォルダパス取得（可視化）
        folder = Common.k_core_v_path(k_core_i_path=k_kore_folder)

        # ボット・リポスト割合まとめ用dataframe
        master_columns = ['Community', 'Classification', 'Percentage']
        data_df = pd.DataFrame(data=None, columns=master_columns)

        # クラスター毎のcsvファイルが存在する場合のみ実行
        if len(glob.glob(k_kore_folder + '/*クラスター.csv')) > 0:
            # クラスターリストを作成（ノード数で降順）
            cluster_list = list(dict.fromkeys(pd.read_csv(k_kore_folder + '/最多リツート.csv',
                                                          dtype=object,
                                                          encoding='utf-16')['Cluster Color'].tolist()))

            file = folder + 'クラスター別ソーシャルボット割合.csv'
            if os.path.exists(file):
                os.remove(file)
            with open(file, 'a', encoding='utf-16') as f:
                writer_object = writer(f)
                writer_object.writerow(['Community', 'Bot_Count', 'Bot_Percentage',
                                        'Human_Count', 'Human_Percentage',
                                        'Bot_Repost_Count', 'Bot_Repost_Percentage',
                                        'Human_Repost_Count', 'Human_Repost_Percentage'])

                for cluster in cluster_list:
                    # ボットアカウントリスト（重複なし）
                    bot_list = []
                    # 人間アカウントリスト（重複なし）
                    human_list = []
                    # 人間・不明アカウントリスト（重複なし）
                    other_list = []
                    # ボットによるリポスト数
                    bot_repost_cnt = 0
                    # 人間によるリポスト数
                    human_repost_cnt = 0
                    # 人間・不明アカウントによるリポスト数
                    other_repost_cnt = 0

                    # クラスター毎のcsvを読み込み
                    df = pd.read_csv(k_kore_folder + '/' + cluster + 'クラスター.csv', dtype=object, encoding='utf-16')

                    # クラスター毎のリツイートを全行読み込み
                    for index, row in df.iterrows():
                        # リツイートを行ったアカウント
                        account = row['Target']
                        # リツイートを行ったアカウントのボットスコア
                        bot_score = round(float(row['Target_Bot_Score']), 2)

                        # ボットの場合
                        if 0.5 <= bot_score <= 1:
                            if account not in bot_list:
                                bot_list.append(account)
                            bot_repost_cnt += 1

                        # ボット以外（人間、不明）の場合
                        else:
                            if account not in other_list:
                                other_list.append(account)
                            other_repost_cnt += 1

                        # 人間の場合
                        if bot_score < 0.5:
                            if account not in human_list:
                                human_list.append(account)
                            human_repost_cnt += 1

                    # クラスター毎にボット・リポスト割合を追加
                    data_df = data_df.dropna(axis=1, how='all')
                    # ボット割合
                    df_append = pd.DataFrame(
                        data=[[cluster, 'bot_account', (len(bot_list) / (len(bot_list) + len(other_list)))*100]],
                        columns=master_columns)
                    data_df = pd.concat([data_df, df_append], ignore_index=True)
                    # リポスト割合
                    df_append = pd.DataFrame(
                        data=[[cluster, 'bot_repost', (bot_repost_cnt / (bot_repost_cnt + other_repost_cnt))*100]],
                        columns=master_columns)
                    data_df = pd.concat([data_df, df_append], ignore_index=True)

                    # 数値をcsvで保存
                    writer_object.writerow([cluster,
                                            len(bot_list),
                                            (len(bot_list) / (len(bot_list) + len(human_list)))*100,
                                            len(human_list),
                                            (len(human_list) / (len(bot_list) + len(human_list)))*100,
                                            bot_repost_cnt,
                                            (bot_repost_cnt / (bot_repost_cnt + human_repost_cnt))*100,
                                            human_repost_cnt,
                                            (human_repost_cnt / (bot_repost_cnt + human_repost_cnt))*100
                                            ])

            # 複数棒グラフを描写
            title = 'Percentage of Socialbots by Cluster'
            title = ''
            Visualization.several_bar_plot_v(title=title,
                                                  x='Community',
                                                  y='Percentage',
                                                  hue='Classification',
                                                  data=data_df,
                                                  palette=['darkgrey', 'lightcoral'],
                                                  file=folder + 'クラスター別ソーシャルボット割合.png')


if __name__ == '__main__':
    repost_by_bot()
