import Common
import Main
import Visualization
from csv import writer
import matplotlib
import numpy as np
import os
import pandas as pd
from scipy.stats import norm
from statsmodels.tsa.stattools import ccf


# 各時間帯のリポスト件数Dataframeを設定
def repost_df(df=None):
    df = df.rename(columns={df.columns[0]: 'Time'})
    df = df.rename(columns={df.columns[1]: 'Count'})
    sub_df = pd.DataFrame()
    for columns in df.columns:
        if columns == 'Time':
            sub_df[columns] = df[columns]
        elif columns == 'Count':
            sub_df[columns] = df[columns].astype(float)
    return sub_df


# 時系列相互相関
def time_series_cross_correlation(file='', data1=None, data2=None):
    # クロス相関の計算（ラグ0から最大ラグまで）
    cross_corr = ccf(data1, data2)[:Main.MAX_LAG]
    # p値の計算
    # サンプルサイズ
    n = len(data1)
    z_scores = cross_corr * np.sqrt(n)  # zスコア計算
    p_values = 2 * (1 - norm.cdf(np.abs(z_scores)))  # 両側検定

    # 結果の出力
    results = pd.DataFrame({
        'Lag': np.arange(Main.MAX_LAG),
        'Cross-Correlation': cross_corr,
        'P-Value': p_values
    })

    # 有意差のあるラグを抽出
    significant_lags = results[results['P-Value'] < 0.05]
    """if os.path.exists(file):
        os.remove(file)"""

    significant_lags.columns = ['時間差',
                                'クロス相関係数（正の値：一方のデータが他方と同じ方向に影響、負の値: 一方のデータが他方と逆方向に影響）',
                                'p値']
    significant_lags.to_csv(file, encoding='utf-16')


# リポスト関係（人間、ソーシャルボット）のエリアチャートと各折れ線グラフの可視化
def relation_visual(file='', repost_rank_list=None, category='', k_kore_folder='', priority='', folder=''):
    df = pd.read_csv(file, dtype=object, encoding='utf-16')
    df = df.astype({'Count': int})
    time_list = df['Time'].tolist()
    df = df.pivot_table(index='Time', columns='Relation', values='Count')

    # クラスター毎に可視化（最初は全体）
    relation_repost_rank_list = repost_rank_list[:]
    relation_repost_rank_list.insert(0, '')
    for color in relation_repost_rank_list:
        # クラスター毎のパスを設定
        path = ''
        # エリアチャートの配色
        color_list = [matplotlib.colormaps['Reds'](0.3), matplotlib.colormaps['Oranges'](0.25),
                      matplotlib.colormaps['Blues'](0.4), matplotlib.colormaps['Greens'](0.25)]
        # 全体
        if color == '':
            # 全体のリポスト関係を抽出
            main_df = df.iloc[:, 0:4]
            # 全体のリポスト件数推移
            sub_file = k_kore_folder + '/リポスト件数推移' + priority + '.csv'
            if os.path.exists(sub_file):
                sub_df1 = pd.read_csv(sub_file, dtype=object, encoding='utf-16')
                # 各時間帯のリポスト件数Dataframeを設定
                sub_df1 = repost_df(sub_df1)
        # クラスター毎
        else:
            # クラスター毎のリポスト関係を抽出
            main_df = df.filter(like=color)
            path = color + '/'
            # クラスター毎のリポスト件数推移
            sub_file = k_kore_folder + '/リポスト推移（範囲内）' + priority + '.csv'
            if os.path.exists(sub_file):
                sub_df1 = pd.read_csv(sub_file, dtype=object, encoding='utf-16')
                sub_df1 = sub_df1.loc[sub_df1['modularity_class'] == color]
                sub_df1 = sub_df1.drop('modularity_class', axis=1)
                sub_df1['Count'] = sub_df1['Count'].astype(float)

            # クラスター毎の感情スコア推移
            sub_file = k_kore_folder + '/感情スコア推移（累計）' + priority + '.csv'
            if os.path.exists(sub_file):
                sub_df5 = pd.read_csv(sub_file, dtype=object, encoding='utf-16')
                # リポスト関係の列名に修正
                main_df.columns = Main.REPOST_RELATION
                # 2軸グラフ描写（リポスト関係エリアチャート + 感情スコア）
                title = color
                Visualization.double_area_v(title=title,
                                                 area_df=main_df,
                                                 plot_list=sub_df5[color].astype(float),
                                                 linestyle=Main.Sentimental_Plot_Style,
                                                 time_list=time_list,
                                                 color_list=color_list,
                                                 plot_label='Emotional Score',
                                                 ax1_y_label='Percentage of Repost Relationships',
                                                 ax2_y_label='Emotional Score',
                                                 invert_yaxis=True,
                                                 file=folder + path + '2軸グラフ（' + category + 'リポスト関係（エリアチャート）・感情スコア）' + priority + '.png')
                # 累計リポスト（リポスト関係100%エリアチャート + 感情スコア）
                main_df2 = main_df.apply(lambda x: x / sum(x), axis=1)
                title = color
                Visualization.double_area_v(title=title,
                                                 area_df=main_df2,
                                                 plot_list=sub_df5[color].astype(float),
                                                 linestyle=Main.Sentimental_Plot_Style,
                                                 time_list=time_list,
                                                 color_list=color_list,
                                                 plot_label='Emotional Score',
                                                 ax1_y_label='Percentage of Repost Relationships',
                                                 ax2_y_label='Emotional Score',
                                                 invert_yaxis=True,
                                                 file=folder + path + '2軸グラフ（' + category + 'リポスト関係（100%エリアチャート）・感情スコア）' + priority + '.png')

                # ソーシャルボットと感情の時系列相互相関
                # ソーシャルボット同士
                b_b = np.array(main_df[Main.REPOST_RELATION[0]])
                b_b = np.nan_to_num(b_b, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボット同士・感情）' + priority + '.csv',
                    data1=b_b,
                    data2=sub_df5[color].astype(float))
                # ソーシャルボットが人間
                b_h = np.array(main_df[Main.REPOST_RELATION[1]])
                b_h = np.nan_to_num(b_h, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボットが人間・感情）' + priority + '.csv',
                    data1=b_h,
                    data2=sub_df5[color].astype(float))
                # 人間がソーシャルボット
                h_b = np.array(main_df[Main.REPOST_RELATION[2]])
                h_b = np.nan_to_num(h_b, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（人間がソーシャルボット・感情）' + priority + '.csv',
                    data1=h_b,
                    data2=sub_df5[color].astype(float))
                # ソーシャルボット関連全体
                b = b_b + b_h + h_b
                b = np.nan_to_num(b, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボット関連全体・感情）' + priority + '.csv',
                    data1=b,
                    data2=sub_df5[color].astype(float))
                # 人間同士
                h_h = np.array(main_df[Main.REPOST_RELATION[3]])
                h_h = np.nan_to_num(h_h, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（人間同士・感情）' + priority + '.csv',
                    data1=h_h,
                    data2=sub_df5[color].astype(float))

                # ソーシャルボットとリポスト件数の時系列相互相関
                # ソーシャルボット同士
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボット同士・リポスト件数）' + priority + '.csv',
                    data1=b_b,
                    data2=sub_df1['Count'])
                # ソーシャルボットが人間
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボットが人間・リポスト件数）' + priority + '.csv',
                    data1=b_h,
                    data2=sub_df1['Count'])
                # 人間がソーシャルボット
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（人間がソーシャルボット・リポスト件数）' + priority + '.csv',
                    data1=h_b,
                    data2=sub_df1['Count'])
                # ソーシャルボット関連全体
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボット関連全体・リポスト件数）' + priority + '.csv',
                    data1=b,
                    data2=sub_df1['Count'])
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（人間同士・リポスト件数）' + priority + '.csv',
                    data1=h_h,
                    data2=sub_df1['Count'])

                # 感情とリポスト件数の時系列相互相関
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（感情・リポスト件数）' + priority + '.csv',
                    data1=sub_df5[color].astype(float),
                    data2=sub_df1['Count'])

                # クラスター内リポスト関係（ソーシャルボット、人間）のカウント
                r_file = folder + path + 'リポスト関係別リポスト数' + priority + '.csv'
                if os.path.exists(r_file):
                    os.remove(r_file)
                with open(r_file, 'a', encoding='utf-16') as r_c:
                    writer_object_r = writer(r_c)
                    writer_object_r.writerow(
                        ['ソーシャルボット同士', 'ソーシャルボットが人間', '人間がソーシャルボット', '人間同士'])
                    writer_object_r.writerow([np.sum(b_b), np.sum(b_h), np.sum(h_b), np.sum(h_h)])
                    r_c.close()

            sub_file = k_kore_folder + '/クラスター間リポスト関係（累計）' + priority + '.csv'
            if os.path.exists(sub_file):
                sub_df2 = pd.read_csv(sub_file, dtype=object, encoding='utf-16')
                sub_df2 = sub_df2.astype({'Count': int})
                sub_df2 = sub_df2.pivot_table(index='Time', columns='Relation', values='Count')

                # クラスター毎のリポスト関係を抽出
                sub_df3 = sub_df2.filter(like=color)
                # 同一クラスター内のリポスト割合を抽出
                sub_df4 = sub_df3.copy()
                sub_df4['Percentage of Repost Relationships'] = (
                        sub_df3[color + '_' + color] /
                        (sub_df3[color + '_' + color] + sub_df3[color + '_others']))
                # リポスト関係の列名に修正
                main_df.columns = Main.REPOST_RELATION
                # 2軸グラフ描写（リポスト関係エリアチャート + 全体のリポスト件数）
                title = color
                Visualization.double_area_v(title=title,
                                                 area_df=main_df,
                                                 plot_list=sub_df4['Percentage of Repost Relationships'],
                                                 linestyle=Main.Echo_Plot_Style,
                                                 time_list=time_list,
                                                 color_list=color_list,
                                                 plot_label='Proportion of Self Repost',
                                                 ax1_y_label='Percentage of Repost Relationships',
                                                 ax2_y_label='Proportion of Self Repost',
                                                 invert_yaxis=False,
                                                 file=folder + path + '2軸グラフ（' + category + 'リポスト関係（エリアチャート）・リポスト関係）' + priority + '.png')
                # 累計リポスト（リポスト関係100%エリアチャート + 全体のリポスト件数）
                main_df2 = main_df.apply(lambda x: x / sum(x), axis=1)
                title = color
                Visualization.double_area_v(title=title,
                                                 area_df=main_df2,
                                                 plot_list=sub_df4['Percentage of Repost Relationships'],
                                                 linestyle=Main.Echo_Plot_Style,
                                                 time_list=time_list,
                                                 color_list=color_list,
                                                 plot_label='Proportion of Self Repost',
                                                 ax1_y_label='Percentage of Repost Relationships',
                                                 ax2_y_label='Proportion of Self Repost',
                                                 invert_yaxis=False,
                                                 file=folder + path + '2軸グラフ（' + category + 'リポスト関係（100%エリアチャート）・リポスト関係）' + priority + '.png')

                # ソーシャルボットとエコーチェンバーの時系列相互相関
                # ソーシャルボット同士
                b_b = np.array(main_df[Main.REPOST_RELATION[0]])
                b_b = np.nan_to_num(b_b, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボット同士・エコーチェンバー）' + priority + '.csv',
                    data1=b_b,
                    data2=sub_df4['Percentage of Repost Relationships'])
                # ソーシャルボットが人間
                b_h = np.array(main_df[Main.REPOST_RELATION[1]])
                b_h = np.nan_to_num(b_h, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボットが人間・エコーチェンバー）' + priority + '.csv',
                    data1=b_h,
                    data2=sub_df4['Percentage of Repost Relationships'])
                # 人間がソーシャルボット
                h_b = np.array(main_df[Main.REPOST_RELATION[2]])
                h_b = np.nan_to_num(h_b, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（人間がソーシャルボット・エコーチェンバー）' + priority + '.csv',
                    data1=h_b,
                    data2=sub_df4['Percentage of Repost Relationships'])
                # ソーシャルボット関連全体
                b = b_b + b_h + h_b
                b = np.nan_to_num(b, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（ソーシャルボット関連全体・エコーチェンバー）' + priority + '.csv',
                    data1=b,
                    data2=sub_df4['Percentage of Repost Relationships'])
                # 人間同士
                h_h = np.array(main_df[Main.REPOST_RELATION[3]])
                h_h = np.nan_to_num(h_h, nan=0.0, posinf=0.0, neginf=0.0)
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（人間同士・エコーチェンバー）' + priority + '.csv',
                    data1=h_h,
                    data2=sub_df4['Percentage of Repost Relationships'])

                # エコーチェンバーとリポスト件数の時系列相互相関
                time_series_cross_correlation(
                    file=folder + color + '/時系列相互相関（エコーチェンバー・リポスト件数）' + priority + '.csv',
                    data1=sub_df4['Percentage of Repost Relationships'],
                    data2=sub_df1['Count'])

            # 4軸グラフ作成（ソーシャルボット（累計、範囲内）、エコーチェンバー（累計）、感情（累計）、リポスト件数（範囲内））
            echo_file = k_kore_folder + '/クラスター間リポスト関係（累計）' + priority + '.csv'
            sentimental_file = k_kore_folder + '/感情スコア推移（累計）' + priority + '.csv'
            repost_file = k_kore_folder + '/リポスト推移（範囲内）' + priority + '.csv'
            if os.path.exists(echo_file) and os.path.exists(sentimental_file) and os.path.exists(repost_file):
                # エコーチェンバー
                echo_df = pd.read_csv(echo_file, dtype=object, encoding='utf-16')
                echo_df = echo_df.astype({'Count': int})
                echo_df = echo_df.pivot_table(index='Time', columns='Relation', values='Count')
                # クラスター毎のリポスト関係を抽出
                echo_df2 = echo_df.filter(like=color)
                # 同一クラスター内のリポスト割合を抽出
                echo_df3 = echo_df2.copy()
                echo_df3['Percentage of Repost Relationships'] = (
                        echo_df2[color + '_' + color] /
                        (echo_df2[color + '_' + color] + echo_df2[color + '_others']))

                # 感情
                sentimental_df = pd.read_csv(sentimental_file, dtype=object, encoding='utf-16')

                # リポスト件数
                repost_sub_df = pd.read_csv(repost_file, dtype=object, encoding='utf-16')
                repost_sub_df = repost_sub_df.loc[repost_sub_df['modularity_class'] == color]
                repost_sub_df = repost_sub_df.drop('modularity_class', axis=1)
                repost_sub_df['Count'] = repost_sub_df['Count'].astype(float)

                # リポスト関係の列名に修正
                main_df.columns = Main.REPOST_RELATION

                # グラフ描写
                main_df2 = main_df.apply(lambda x: x / sum(x), axis=1)
                title = color
                Visualization.quartet_v(title=title,
                                             area_df=main_df2,

                                             plot_list1=echo_df3['Percentage of Repost Relationships'],
                                             linestyle1=Main.Echo_Plot_Style,
                                             plot_label1='Proportion of Self Repost',
                                             linecolor1='green',
                                             linewidth1=1.5,

                                             plot_list2=sentimental_df[color].astype(float),
                                             linestyle2=Main.Sentimental_Plot_Style,
                                             plot_label2='Emotional Score',
                                             linecolor2='blue',
                                             linewidth2=1.5,

                                             plot_list3=repost_sub_df['Count'],
                                             linestyle3=Main.Repost_Plot_Style,
                                             plot_label3='Repost',
                                             linecolor3='red',
                                             linewidth3=1,

                                             ax1_y_label='Percentage of Repost Relationships',
                                             ax2_y_label='Proportion of Self Repost',
                                             ax3_y_label='Emotional Score',
                                             ax4_y_label='Repost',

                                             time_list=time_list,
                                             color_list=color_list,
                                             invert_yaxis=True,
                                             file=folder + path + '4軸グラフ（' + category +
                                                  'リポスト関係（100%エリアチャート）・リポスト関係・感情スコア・リポスト数）' +
                                                  priority + '.png')

        # リポスト関係の列名に修正
        main_df.columns = Main.REPOST_RELATION
        # 2軸グラフ描写（リポスト関係エリアチャート + リポスト件数）
        title = color
        Visualization.double_area_v(title=title,
                                         area_df=main_df,
                                         plot_list=sub_df1['Count'],
                                         linestyle=Main.Repost_Plot_Style,
                                         time_list=time_list,
                                         color_list=color_list,
                                         plot_label='Repost',
                                         ax1_y_label='Percentage of Repost Relationships',
                                         ax2_y_label='Repost',
                                         invert_yaxis=False,
                                         file=folder + path + '2軸グラフ（' + category + 'リポスト関係（エリアチャート）・リポスト数）' + priority + '.png')
        # 累計リポスト（リポスト関係100%エリアチャート + リポスト件数）
        main_df2 = main_df.apply(lambda x: x / sum(x), axis=1)
        title = color
        Visualization.double_area_v(title=title,
                                         area_df=main_df2,
                                         plot_list=sub_df1['Count'],
                                         linestyle=Main.Repost_Plot_Style,
                                         time_list=time_list,
                                         color_list=color_list,
                                         plot_label='Repost',
                                         ax1_y_label='Percentage of Repost Relationships',
                                         ax2_y_label='Repost',
                                         invert_yaxis=False,
                                         file=folder + path + '2軸グラフ（' + category + 'リポスト関係（100%エリアチャート）・リポスト数）' + priority + '.png')


# 時系列可視化
def date_time(priority=''):
    print(Common.now() + '　時系列可視化開始' + priority, flush=True)

    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():

        # リポスト数ランキングリスト（リツイート数（クラスター別）.csvが無い場合、可視化は行わない）
        file = k_kore_folder + '/リツイート数（クラスター別）.csv'
        if os.path.exists(file):
            repost_rank_list = pd.read_csv(file,
                                           dtype=object,
                                           encoding='utf-16')['modularity_class'].tolist()

            # kコア分解毎のフォルダパス取得（可視化）
            folder = Common.k_core_v_path(k_core_i_path=k_kore_folder)

            # 累計リポスト（エリアチャート）
            file = k_kore_folder + '/リポスト推移（累計）' + priority + '.csv'
            if os.path.exists(file):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                df = df.astype({'Count': int})
                df = df.pivot_table(index='Time', columns='modularity_class', values='Count')
                df = df.reindex(columns=repost_rank_list)
                # 累計リポスト（エリアチャート）
                title = 'Cumulative Repost(Count)'
                title = ''
                Visualization.area_v(title=title,
                                          df=df,
                                          color=repost_rank_list,
                                          file=folder + '累計リポスト（エリアチャート）' + priority + '.png')
                # 累計リポスト（100%エリアチャート）
                df = df.apply(lambda x: x / sum(x), axis=1)
                title = 'Cumulative Repost(Percentage)'
                title = ''
                Visualization.area_v(title=title,
                                          df=df,
                                          color=repost_rank_list,
                                          file=folder + '累計リポスト（100%エリアチャート）' + priority + '.png')

            # リポスト関係推移（エリアチャート）
            # リポスト関係（人間、ソーシャルボット）のエリアチャートと各折れ線グラフの可視化
            """file = k_kore_folder + '/リポスト関係（累計）' + priority + '.csv'
            if os.path.exists(file):
                relation_visual(file=file, repost_rank_list=repost_rank_list, category='累計',
                                k_kore_folder=k_kore_folder, priority=priority, folder=folder)"""
            file = k_kore_folder + '/リポスト関係（範囲内）' + priority + '.csv'
            if os.path.exists(file):
                relation_visual(file=file, repost_rank_list=repost_rank_list, category='範囲内',
                                k_kore_folder=k_kore_folder, priority=priority, folder=folder)

            # クラスター間リポスト関係推移
            file = k_kore_folder + '/クラスター間リポスト関係（累計）' + priority + '.csv'
            # リポスト推移
            repost_csv = k_kore_folder + '/リポスト推移（範囲内）' + priority + '.csv'
            if os.path.exists(file) and os.path.exists(repost_csv):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                df = df.astype({'Count': int})

                all_repost_df = pd.read_csv(repost_csv, dtype=object, encoding='utf-16')

                time_list = list(dict.fromkeys(df['Time'].tolist()))
                df = df.pivot_table(index='Time', columns='Relation', values='Count')
                # クラスター毎に可視化
                for color in repost_rank_list:
                    # クラスター毎のリポスト関係を抽出
                    sub_df = df.filter(like=color)
                    # クラスター毎のリポスト件数を抽出
                    repost_sub_df = all_repost_df.loc[all_repost_df['modularity_class'] == color]
                    repost_sub_df = repost_sub_df['Count']
                    repost_sub_df = repost_sub_df.astype(int)

                    # 連結DataFrame
                    connection_df = sub_df.copy()
                    connection_df['Proportion of Self Repost'] = (
                            sub_df[color + '_' + color] / (sub_df[color + '_' + color] + sub_df[color + '_others']))
                    connection_df['Repost'] = repost_sub_df.values

                    title = color
                    Visualization.double_plot_v(title=title,
                                                     connection_df=connection_df,
                                                     time_list=time_list,
                                                     linestyle1=Main.Echo_Plot_Style,
                                                     linestyle2=Main.Repost_Plot_Style,
                                                     line_color=color,
                                                     bar_color='black',
                                                     line_columns='Proportion of Self Repost',
                                                     bar_columns='Repost',
                                                     ax1_y_label='Proportion of Self Repost',
                                                     ax2_y_label='Repost',
                                                     invert_yaxis1=False,
                                                     invert_yaxis2=False,
                                                     file=folder + color + '/2軸グラフ（リポスト数・クラスター間リポスト関係）' + priority + '.png')

            # 感情スコア推移
            file = k_kore_folder + '/感情スコア推移（累計）' + priority + '.csv'
            # リポスト推移
            repost_csv = k_kore_folder + '/リポスト推移（範囲内）' + priority + '.csv'
            if os.path.exists(file) and os.path.exists(repost_csv):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                all_repost_df = pd.read_csv(repost_csv, dtype=object, encoding='utf-16')

                time_list = list(dict.fromkeys(all_repost_df['Time'].tolist()))
                # クラスター毎に可視化
                for color in repost_rank_list:
                    # クラスター毎の感情スコアを抽出
                    df[color] = df[color].astype(float)
                    sub_df = df.filter(like=color)
                    sub_df = sub_df.rename(columns={sub_df.columns[0]: 'Emotional Score'})
                    # クラスター毎のリポスト件数を抽出
                    repost_sub_df = all_repost_df.loc[all_repost_df['modularity_class'] == color]
                    repost_sub_df = repost_sub_df['Count']
                    repost_sub_df = repost_sub_df.astype(int)

                    # 連結DataFrame
                    connection_df = sub_df.copy()
                    connection_df['Repost'] = repost_sub_df.values

                    title = color
                    Visualization.double_plot_v(title=title,
                                                     connection_df=connection_df,
                                                     time_list=time_list,
                                                     linestyle1=Main.Sentimental_Plot_Style,
                                                     linestyle2=Main.Repost_Plot_Style,
                                                     line_color=color,
                                                     bar_color='black',
                                                     line_columns='Emotional Score',
                                                     bar_columns='Repost',
                                                     ax1_y_label='Emotional Score',
                                                     ax2_y_label='Repost',
                                                     invert_yaxis1=True,
                                                     invert_yaxis2=False,
                                                     file=folder + color + '/2軸グラフ（感情スコア・リポスト数）' + priority + '.png')

            # クラスター間リポスト関係推移
            file = k_kore_folder + '/クラスター間リポスト関係（累計）' + priority + '.csv'
            # 感情スコア推移
            sentimental_file = k_kore_folder + '/感情スコア推移（累計）' + priority + '.csv'
            if os.path.exists(file) and os.path.exists(sentimental_file):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                df = df.astype({'Count': int})
                df = df.pivot_table(index='Time', columns='Relation', values='Count')
                sentimental_df = pd.read_csv(sentimental_file, dtype=object, encoding='utf-16')
                sentimental_df = sentimental_df.rename(columns={sentimental_df.columns[0]: 'Time'})

                time_list = list(dict.fromkeys(sentimental_df['Time'].tolist()))
                # クラスター毎に可視化
                for color in repost_rank_list:
                    # クラスター毎のリポスト関係を抽出
                    sub_df = df.filter(like=color)
                    # クラスター毎の感情スコアを抽出
                    sentimental_df[color] = sentimental_df[color].astype(float)
                    sub_df2 = sentimental_df.filter(like=color)
                    sub_df2 = sub_df2.rename(columns={sub_df2.columns[0]: 'Emotional Score'})

                    # 連結DataFrame
                    connection_df = sub_df.copy()
                    connection_df['Proportion of Self Repost'] = (
                            sub_df[color + '_' + color] / (sub_df[color + '_' + color] + sub_df[color + '_others']))
                    connection_df['Emotional Score'] = sub_df2.values

                    title = color
                    Visualization.double_plot_v(title=title,
                                                     connection_df=connection_df,
                                                     time_list=time_list,
                                                     linestyle1=Main.Echo_Plot_Style,
                                                     linestyle2=Main.Sentimental_Plot_Style,
                                                     line_color='black',
                                                     bar_color=color,
                                                     line_columns='Proportion of Self Repost',
                                                     bar_columns='Emotional Score',
                                                     ax1_y_label='Proportion of Self Repost',
                                                     ax2_y_label='Emotional Score',
                                                     invert_yaxis1=False,
                                                     invert_yaxis2=True,
                                                     file=folder + color + '/2軸グラフ（クラスター間リポスト関係・感情スコア）' + priority + '.png')
                    # エコーチェンバーと感情の時系列相互相関
                    time_series_cross_correlation(file=folder + color + '/時系列相互相関（エコーチェンバー・感情）' + priority + '.csv',
                                                  data1=connection_df['Proportion of Self Repost'],
                                                  data2=connection_df['Emotional Score'])
                    # 感情とエコーチェンバーの時系列相互相関
                    time_series_cross_correlation(file=folder + color + '/時系列相互相関（感情・エコーチェンバー）' + priority + '.csv',
                                                  data1=connection_df['Emotional Score'],
                                                  data2=connection_df['Proportion of Self Repost'])

            # クラスター係数推移
            file = k_kore_folder + '/クラスター係数推移' + priority + '.csv'
            if os.path.exists(file):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                df = df.rename(columns={df.columns[0]: 'Time'})
                sub_df = pd.DataFrame()
                for cluster in df.columns:
                    if cluster == 'Time':
                        sub_df[cluster] = df[cluster]
                    else:
                        sub_df[cluster] = df[cluster].astype(float)
                title = 'Clustering Coefficient Transition'
                title = ''
                Visualization.line_v(title=title,
                                          df=sub_df,
                                          linestyle=Main.Coefficient_Plot_Style,
                                          x_ticks=sub_df['Time'].tolist(),
                                          repost_rank_list=repost_rank_list,
                                          lw=2,
                                          invert_yaxis=False,
                                          legend=True,
                                          file=folder + 'クラスター係数推移' + priority + '.png')

            # 感情スコア推移
            file = k_kore_folder + '/感情スコア推移（累計）' + priority + '.csv'
            if os.path.exists(file):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                df = df.rename(columns={df.columns[0]: 'Time'})
                sub_df = pd.DataFrame()
                for cluster in df.columns:
                    if cluster == 'Time':
                        sub_df[cluster] = df[cluster]
                    else:
                        sub_df[cluster] = df[cluster].astype(float)
                title = 'Emotional Score Transition'
                title = ''
                Visualization.line_v(title=title,
                                          df=sub_df,
                                          linestyle=Main.Sentimental_Plot_Style,
                                          x_ticks=sub_df['Time'].tolist(),
                                          repost_rank_list=repost_rank_list,
                                          lw=1,
                                          invert_yaxis=True,
                                          legend=True,
                                          file=folder + '感情スコア推移' + priority + '.png')

            # リポスト件数推移
            file = k_kore_folder + '/リポスト件数推移' + priority + '.csv'
            if os.path.exists(file):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                # 各時間帯のリポスト件数Dataframeを設定
                sub_df = repost_df(df)
                title = 'Repost Transition'
                title = ''
                Visualization.line_v(title=title,
                                          df=sub_df,
                                          linestyle=Main.Repost_Plot_Style,
                                          x_ticks=sub_df['Time'].tolist(),
                                          repost_rank_list='black',
                                          lw=0.5,
                                          invert_yaxis=False,
                                          legend=False,
                                          file=folder + 'リポスト件数推移' + priority + '.png')

            # リポスト件数推移（クラスター別））
            file = k_kore_folder + '/リポスト件数推移（クラスター別）' + priority + '.csv'
            if os.path.exists(file):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                df = df.rename(columns={df.columns[0]: 'Time'})
                sub_df = pd.DataFrame()
                for cluster in df.columns:
                    if cluster == 'Time':
                        sub_df[cluster] = df[cluster]
                    else:
                        sub_df[cluster] = df[cluster].astype(float)
                title = 'Repost Transition'
                title = ''
                Visualization.line_v(title=title,
                                          df=sub_df,
                                          linestyle=Main.Repost_Plot_Style,
                                          x_ticks=sub_df['Time'].tolist(),
                                          repost_rank_list=repost_rank_list,
                                          lw=0.5,
                                          invert_yaxis=False,
                                          legend=True,
                                          file=folder + 'リポスト件数推移（クラスター別）' + priority + '.png')

            # リポスト増加件数推移
            file = k_kore_folder + '/リポスト増加件数推移' + priority + '.csv'
            if os.path.exists(file):
                df = pd.read_csv(file, dtype=object, encoding='utf-16')
                df = df.rename(columns={df.columns[0]: 'Time'})
                sub_df = pd.DataFrame()
                for cluster in df.columns:
                    if cluster == 'Time':
                        sub_df[cluster] = df[cluster]
                    else:
                        sub_df[cluster] = df[cluster].astype(float)
                title = 'Repost Increase Transition'
                title = ''
                Visualization.line_v(title=title,
                                          df=sub_df,
                                          linestyle=Main.Repost_Plot_Style,
                                          x_ticks=sub_df['Time'].tolist(),
                                          repost_rank_list='black',
                                          lw=0.5,
                                          invert_yaxis=False,
                                          legend=False,
                                          file=folder + 'リポスト増加件数推移' + priority + '.png')


if __name__ == '__main__':
    date_time(priority='')
    date_time(priority='（重点分析期間）')
