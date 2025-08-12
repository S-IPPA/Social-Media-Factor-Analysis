import Common
import Main
import datetime
from datetime import timedelta
import glob
import networkx as nx
import pandas as pd


# リポスト関係DataFrameの該当件数をカウントアップ
def repost_relation(repost_account=None, reposted_account=None, df=None, statement_time='', modularity_class=''):
    relation = ''
    # ボット間でのリポスト
    if 0.5 <= repost_account <= 1 and 0.5 <= reposted_account <= 1:
        relation = Main.REPOST_RELATION[0]
    # ボットが人間をリポスト
    if 0.5 <= repost_account <= 1 and reposted_account < 0.5:
        relation = Main.REPOST_RELATION[1]
    # 人間がボットをリポスト
    if repost_account < 0.5 and 0.5 <= reposted_account <= 1:
        relation = Main.REPOST_RELATION[2]
    # 人間間でのリポスト
    if repost_account < 0.5 and reposted_account < 0.5:
        relation = Main.REPOST_RELATION[3]
    # 全体
    query_str = ('Time == "Replace1" and Relation == "Replace2"'
                 .replace('Replace1', statement_time)
                 .replace('Replace2', relation))
    df_subset = df.query(query_str)
    df.loc[df_subset.index, 'Count'] += 1
    # クラスター別
    query_str = ('Time == "Replace1" and Relation == "Replace2"'
                 .replace('Replace1', statement_time)
                 .replace('Replace2', modularity_class + '_' + relation))
    df_subset = df.query(query_str)
    df.loc[df_subset.index, 'Count'] += 1

    return df


# クラスター間リポスト関係DataFrameの該当件数をカウントアップ
def community_relation(repost_account_community=None, reposted_account_community=None, df=None, statement_time=''):
    # 同一クラスター間（エコーチェンバー）
    if repost_account_community == reposted_account_community:
        query_str = ('Time == "Replace1" and Relation == "Replace2"'
                     .replace('Replace1', statement_time)
                     .replace('Replace2', repost_account_community + '_' + reposted_account_community))
        df_subset = df.query(query_str)
        df.loc[df_subset.index, 'Count'] += 1
    # 別クラスター間
    else:
        query_str = ('Time == "Replace1" and Relation == "Replace2"'
                     .replace('Replace1', statement_time)
                     .replace('Replace2', repost_account_community + '_others'))
        df_subset = df.query(query_str)
        df.loc[df_subset.index, 'Count'] += 1
        query_str = ('Time == "Replace1" and Relation == "Replace2"'
                     .replace('Replace1', statement_time)
                     .replace('Replace2', reposted_account_community + '_others'))
        df_subset = df.query(query_str)
        df.loc[df_subset.index, 'Count'] += 1

    return df


# 時系列分析
def date_time():
    print(Common.now() + '　時系列分析開始', flush=True)

    # kコア分解のフォルダを全取得
    for k_kore_folder in Common.k_kore_folder_get():
        # 各kコア分解フォルダ内のリツイートcsv（クラスター毎）を取得
        cluster_csv_list = glob.glob(k_kore_folder + '/*クラスター.csv')
        # クラスター毎のcsvファイルが存在する場合のみ実行
        if len(cluster_csv_list) > 0:
            k_kore = k_kore_folder.split('/')[-1]
            print(Common.now() + '　　kコア分解：' + k_kore.replace('kコア分解', ''), flush=True)

            # リポスト数ランキングリスト
            repost_rank_list = pd.read_csv(k_kore_folder + '/リツイート数（クラスター別）.csv',
                                           dtype=object,
                                           encoding='utf-16')['modularity_class'].tolist()

            # ノード配色dictを作成
            color_dict = Common.node_color_dict(k_kore_folder=k_kore_folder)

            # マスターcsvからリツイートを抽出
            sub_df = Common.re_df()
            sub_df['Time'] = pd.to_datetime(sub_df['Time'])

            # 連結DataFrame
            connection_df = pd.DataFrame()
            # クラスター毎に実行
            for cluster_csv in cluster_csv_list:
                # クラスターカラー取得
                color = Common.color_get(cluster_csv=cluster_csv)

                # クラスター毎のcsvファイル
                cluster_df = pd.read_csv(cluster_csv, dtype=object, encoding='utf-16')
                # 文章を削除
                cluster_df.drop(columns=['Text'], inplace=True)
                # クラスターカラーを追加
                cluster_df['modularity_class'] = color

                # DataFrameを垂直に連結する
                connection_df = pd.concat([connection_df, cluster_df])

            # 日時を昇順にソート
            connection_df = connection_df.sort_values(by='Time', ascending=True)
            connection_df['Time'] = pd.to_datetime(connection_df['Time'])

            # csvを保存
            print(Common.now() + '　　　csvを保存（連結・日時昇順）', flush=True)
            connection_df.to_csv(k_kore_folder + '/日時昇順リツイート（クラスター追記）.csv', encoding='utf-16')

            # リポスト件数用dataframeカラム
            total_df_columns = ['Time', 'modularity_class', 'Count']
            # 範囲内用dataframe
            interval_df = pd.DataFrame(data=None, columns=total_df_columns)
            # 累計用dataframe
            total_df = pd.DataFrame(data=None, columns=total_df_columns)

            # リポスト関係用dataframeカラム
            relation_df_columns = ['Time', 'Relation', 'Count']
            # リポスト関係範囲内用dataframe
            relation_interval_df = pd.DataFrame(data=None, columns=relation_df_columns)
            # リポスト関係累計用dataframe
            relation_total_df = pd.DataFrame(data=None, columns=relation_df_columns)

            # クラスター間リポスト用dataframeカラム
            community_df_columns = ['Time', 'Relation', 'Count']
            # リポスト関係範囲内用dataframe
            community_interval_df = pd.DataFrame(data=None, columns=community_df_columns)
            # リポスト関係累計用dataframe
            community_total_df = pd.DataFrame(data=None, columns=community_df_columns)

            # クラスター係数用dict
            clustering_coefficient_dict = {}
            # クラスター係数算出用dict
            clustering_coefficient_path_dict = {}
            # 感情スコア範囲内用dict
            sentimental_interval_dict = {}
            # 感情スコア累計用dict
            sentimental_total_dict = {}
            # 感情スコア範囲内算出用dict
            sentimental_interval_path_dict = {}
            # 感情スコア累計算出用dict
            sentimental_total_path_dict = {}

            # リポスト件数用dict
            repost_dict = {}
            # クラスター別リポスト件数用dict
            repost_cluster_dict = {}
            # リポスト件数増加用dict
            repost_increase_dict = {}

            # リポスト件数増加用dataframe
            repost_increase_df = pd.DataFrame(data=None, columns=total_df_columns)

            # 対象時間範囲（開始、不変：累計に使用）
            start_time = datetime.datetime.strptime(Main.START_DATE, '%Y/%m/%d %H:%M:%S')

            # 対象時間範囲（開始、終了）
            # クラスター間リポスト以外分析用（対象時間範囲を再設定）
            range_start_time = datetime.datetime.strptime(Main.START_DATE, '%Y/%m/%d %H:%M:%S')
            range_end_time = start_time + timedelta(minutes=59, seconds=59)
            end_flg = 0
            while True:
                if range_start_time > datetime.datetime.strptime(Main.END_DATE, '%Y/%m/%d %H:%M:%S'):
                    break
                # データ分析終了日時が設定され、当該日時を超える場合
                if end_flg == 0:
                    if (Main.ANALYSIS_END_DATE != '' and
                            range_start_time > datetime.datetime.strptime(
                                Main.ANALYSIS_END_DATE, '%Y/%m/%d %H:%M:%S')):
                        end_flg = 1
                        # リポスト推移（範囲内）
                        print(Common.now() + '　　　　　csvを保存（リポスト推移（範囲内）（重点分析期間））', flush=True)
                        interval_df.to_csv(k_kore_folder + '/リポスト推移（範囲内）（重点分析期間）.csv', encoding='utf-16')
                        # リポスト推移（累計）
                        print(Common.now() + '　　　　　csvを保存（リポスト推移（累計）（重点分析期間））', flush=True)
                        total_df.to_csv(k_kore_folder + '/リポスト推移（累計）（重点分析期間）.csv', encoding='utf-16')
                        # 感情スコア推移（範囲内）
                        print(Common.now() + '　　　　　csvを保存（感情スコア推移（範囲内）（重点分析期間））', flush=True)
                        # keyを行ラベル、valueを列ラベル
                        sentimental_interval_df = pd.DataFrame.from_dict(sentimental_interval_dict, orient='index')
                        sentimental_interval_df.columns = repost_rank_list
                        sentimental_interval_df.to_csv(k_kore_folder + '/感情スコア推移（範囲内）（重点分析期間）.csv', encoding='utf-16')
                        # 感情スコア推移（累計）
                        print(Common.now() + '　　　　　csvを保存（感情スコア推移（累計）（重点分析期間））', flush=True)
                        # keyを行ラベル、valueを列ラベル
                        sentimental_total_df = pd.DataFrame.from_dict(sentimental_total_dict, orient='index')
                        sentimental_total_df.columns = repost_rank_list
                        sentimental_total_df.to_csv(k_kore_folder + '/感情スコア推移（累計）（重点分析期間）.csv', encoding='utf-16')
                        # リポスト関係（範囲内）
                        print(Common.now() + '　　　　　csvを保存（リポスト関係（範囲内）（重点分析期間））', flush=True)
                        relation_interval_df.to_csv(k_kore_folder + '/リポスト関係（範囲内）（重点分析期間）.csv', encoding='utf-16')
                        # リポスト関係（累計）
                        print(Common.now() + '　　　　　csvを保存（リポスト関係（累計）（重点分析期間））', flush=True)
                        relation_total_df.to_csv(k_kore_folder + '/リポスト関係（累計）（重点分析期間）.csv', encoding='utf-16')
                        # クラスター係数推移
                        print(Common.now() + '　　　　　csvを保存（クラスター係数推移）（重点分析期間）', flush=True)
                        # keyを行ラベル、valueを列ラベル
                        clustering_coefficient_df = pd.DataFrame.from_dict(clustering_coefficient_dict, orient='index')
                        clustering_coefficient_df.columns = repost_rank_list
                        clustering_coefficient_df.to_csv(k_kore_folder + '/クラスター係数推移（重点分析期間）.csv', encoding='utf-16')
                        # リポスト件数推移
                        print(Common.now() + '　　　　　csvを保存（リポスト件数推移）（重点分析期間）', flush=True)
                        (pd.DataFrame.from_dict(repost_dict, orient='index')
                         .to_csv(k_kore_folder + '/リポスト件数推移（重点分析期間）.csv', encoding='utf-16'))
                        # リポスト件数推移（クラスター別）
                        print(Common.now() + '　　　　　csvを保存（リポスト件数推移（クラスター別）（重点分析期間））', flush=True)
                        # keyを行ラベル、valueを列ラベル
                        repost_cluster_df = pd.DataFrame.from_dict(repost_cluster_dict, orient='index')
                        repost_cluster_df.columns = repost_rank_list
                        repost_cluster_df.to_csv(k_kore_folder + '/リポスト件数推移（クラスター別）（重点分析期間）.csv', encoding='utf-16')
                        # リポスト増加件数推移
                        print(Common.now() + '　　　　　csvを保存（リポスト増加件数推移）（重点分析期間）', flush=True)
                        (pd.DataFrame.from_dict(repost_increase_dict, orient='index')
                         .to_csv(k_kore_folder + '/リポスト増加件数推移（重点分析期間）.csv', encoding='utf-16'))
                        # リポスト増加件数推移（クラスター別）
                        print(Common.now() + '　　　　　csvを保存（リポスト増加件数推移（クラスター別）（重点分析期間））', flush=True)
                        repost_increase_df.to_csv(k_kore_folder + '/リポスト増加件数推移（クラスター別）（重点分析期間）.csv',
                                                  encoding='utf-16')
                        # クラスター間リポスト関係（範囲内）
                        print(Common.now() + '　　　　　csvを保存（クラスター間リポスト関係（範囲内）（重点分析期間））',
                              flush=True)
                        community_interval_df.to_csv(
                            k_kore_folder + '/クラスター間リポスト関係（範囲内）（重点分析期間）.csv',
                            encoding='utf-16')
                        # クラスター間リポスト関係（累計）
                        print(Common.now() + '　　　　　csvを保存（クラスター間リポスト関係（累計）（重点分析期間））',
                              flush=True)
                        community_total_df.to_csv(k_kore_folder + '/クラスター間リポスト関係（累計）（重点分析期間）.csv',
                                                  encoding='utf-16')
                # 対象時間帯
                statement_time = datetime.datetime.strftime(range_start_time, '%m/%d %H') + '時'
                print(Common.now() + '　　　　対象時間帯：' + statement_time, flush=True)
                # 対象時間範囲の各関係のリポスト数等を設定（初期値：0）
                # 全体
                for relation in Main.REPOST_RELATION:
                    df_append = pd.DataFrame(data=[[statement_time, relation, 0]], columns=relation_df_columns)
                    relation_interval_df = pd.concat([relation_interval_df, df_append], ignore_index=True)
                    relation_total_df = pd.concat([relation_total_df, df_append], ignore_index=True)
                # 対象時間範囲の各クラスターのリポスト数・増加件数を設定（初期値：0）
                for cluster in repost_rank_list:
                    df_append = pd.DataFrame(data=[[statement_time, cluster, 0]], columns=total_df_columns)
                    interval_df = pd.concat([interval_df, df_append], ignore_index=True)
                    total_df = pd.concat([total_df, df_append], ignore_index=True)
                    repost_increase_df = pd.concat([repost_increase_df, df_append], ignore_index=True)

                    # 同一クラスター間（エコーチェンバー）
                    df_append = pd.DataFrame(data=[[statement_time, cluster + '_' + cluster, 0]],
                                             columns=community_df_columns)
                    community_interval_df = pd.concat([community_interval_df, df_append], ignore_index=True)
                    community_total_df = pd.concat([community_total_df, df_append], ignore_index=True)
                    # 別クラスター間
                    df_append = pd.DataFrame(data=[[statement_time, cluster + '_others', 0]],
                                             columns=community_df_columns)
                    community_interval_df = pd.concat([community_interval_df, df_append], ignore_index=True)
                    community_total_df = pd.concat([community_total_df, df_append], ignore_index=True)

                    # 対象時間範囲の各関係のリポスト数を設定（初期値：0）
                    for relation in Main.REPOST_RELATION:
                        df_append = pd.DataFrame(data=[[statement_time, cluster + '_' + relation, 0]],
                                                 columns=relation_df_columns)
                        relation_interval_df = pd.concat([relation_interval_df, df_append], ignore_index=True)
                        relation_total_df = pd.concat([relation_total_df, df_append], ignore_index=True)

                    # クラスター係数算出用dict
                    clustering_coefficient_path_dict[cluster] = []
                    # 感情スコア累計算出用dict
                    sentimental_total_path_dict[cluster] = []
                    # 感情スコア範囲内算出用dict
                    sentimental_interval_path_dict[cluster] = []

                # 対象時間範囲のリポスト件数を設定（初期値：0）
                repost_dict[statement_time] = 0

                # 連結DataFrameを全行読み込み
                for index, row in connection_df.iterrows():
                    time = row['Time']
                    statement_modularity_class = row['modularity_class']
                    repost_account_score = round(float(row['Target_Bot_Score']), 2)
                    reposted_account_score = round(float(row['Source_Bot_Score']), 2)
                    # 設定対象クエリー（リポスト件数）
                    query_str = ('Time == "Replace1" and modularity_class == "Replace2"'
                                 .replace('Replace1', statement_time)
                                 .replace('Replace2', statement_modularity_class))
                    # 対象時間範囲内の場合（累計）
                    if start_time <= time <= range_end_time:
                        # リポスト件数
                        df_subset = total_df.query(query_str)
                        total_df.loc[df_subset.index, 'Count'] += 1
                        # リポスト関係
                        relation_total_df = repost_relation(repost_account=repost_account_score,
                                                            reposted_account=reposted_account_score,
                                                            df=relation_total_df,
                                                            statement_time=statement_time,
                                                            modularity_class=statement_modularity_class)
                        # クラスター係数算出用dict
                        clustering_coefficient_path_dict[row['modularity_class']].append((row['Source'], row['Target']))
                        # 感情スコア累計算出用dict
                        sentimental_total_path_dict[row['modularity_class']].append(
                            round(float(row['Sentimental_Score']), 2))

                    # 対象時間範囲内の場合（1時間以内）
                    if range_start_time <= time <= range_end_time:
                        # リポスト件数
                        df_subset = interval_df.query(query_str)
                        interval_df.loc[df_subset.index, 'Count'] += 1
                        # リポスト関係
                        relation_interval_df = repost_relation(repost_account=repost_account_score,
                                                               reposted_account=reposted_account_score,
                                                               df=relation_interval_df,
                                                               statement_time=statement_time,
                                                               modularity_class=statement_modularity_class)
                        # 感情スコア範囲内算出用dict
                        sentimental_interval_path_dict[row['modularity_class']].append(
                            round(float(row['Sentimental_Score']), 2))
                        # 対象時間範囲のリポスト件数をカウントアップ
                        repost_dict[statement_time] += 1

                # リツイートを全行読み込み
                for index, row in sub_df.iterrows():
                    time = row['Time']
                    repost_account = row['User_Id']
                    reposted_account = row['To_ReTweet']
                    if repost_account in color_dict.keys() and reposted_account in color_dict.keys():
                        # 対象時間範囲内の場合（累計）
                        if start_time <= time <= range_end_time:
                            community_total_df = (
                                community_relation(repost_account_community=color_dict[repost_account],
                                                   reposted_account_community=color_dict[reposted_account],
                                                   df=community_total_df,
                                                   statement_time=statement_time))
                        # 対象時間範囲内の場合（1時間以内）
                        if range_start_time <= time <= range_end_time:
                            # クラスター間リポスト関係
                            community_interval_df = (
                                community_relation(repost_account_community=color_dict[repost_account],
                                                   reposted_account_community=color_dict[reposted_account],
                                                   df=community_interval_df,
                                                   statement_time=statement_time))

                # 対象時間範囲のリポスト件数（クラスター別）を設定
                repost_cluster_dict[statement_time] = []
                for cluster in repost_rank_list:
                    query_str = ('Time == "Replace1" and modularity_class == "Replace2"'
                                 .replace('Replace1', statement_time)
                                 .replace('Replace2', cluster))
                    repost_cluster_dict[statement_time].append(interval_df.query(query_str)['Count'].iloc[-1])
                # 対象時間範囲内（累計）のクラスター係数、感情スコアを算出
                clustering_coefficient_dict[statement_time] = []
                sentimental_total_dict[statement_time] = []
                sentimental_interval_dict[statement_time] = []

                for cluster in repost_rank_list:
                    # 該当クラスターのパスが存在
                    if clustering_coefficient_path_dict[cluster]:
                        G = nx.DiGraph()
                        G.add_edges_from(clustering_coefficient_path_dict[cluster])
                        clustering_coefficient = nx.average_clustering(G)
                    # 該当クラスターのパスが存在せず
                    else:
                        clustering_coefficient = 0
                    clustering_coefficient_dict[statement_time].append(clustering_coefficient)
                    # 該当クラスターの感情スコアが存在（累計）
                    if sentimental_total_path_dict[cluster]:
                        sentimental_score = (
                                sum(sentimental_total_path_dict[cluster]) /
                                len(sentimental_total_path_dict[cluster]))
                    # 該当クラスターのパスが存在せず
                    else:
                        sentimental_score = 0
                    sentimental_total_dict[statement_time].append(sentimental_score)
                    # 該当クラスターの感情スコアが存在（1時間以内）
                    if sentimental_interval_path_dict[cluster]:
                        sentimental_score = (
                                sum(sentimental_interval_path_dict[cluster]) /
                                len(sentimental_interval_path_dict[cluster]))
                    # 該当クラスターのパスが存在せず
                    else:
                        sentimental_score = 0
                    sentimental_interval_dict[statement_time].append(sentimental_score)

                # 対象時間範囲のリポスト増加件数を設定
                # 最初の時間帯
                if len(repost_dict.keys()) == 1:
                    increase_reposts = repost_dict[statement_time]
                else:
                    previous_index = list(repost_dict).index(statement_time) - 1
                    # 前時間帯のリポスト件数
                    previous_reposts = repost_dict[list(repost_dict)[previous_index]]
                    # 前時間帯からの増加リポスト件数
                    increase_reposts = repost_dict[statement_time] - previous_reposts
                repost_increase_dict[statement_time] = increase_reposts
                # 対象時間範囲のリポスト増加件数を設定（クラスター別）
                for cluster in repost_rank_list:
                    query_str = ('Time == "Replace1" and modularity_class == "Replace2"'
                                 .replace('Replace1', statement_time)
                                 .replace('Replace2', cluster))
                    df_subset = interval_df.query(query_str)
                    # 最初の時間帯
                    if len(interval_df['modularity_class'].tolist()) == len(repost_rank_list):
                        increase_reposts = df_subset['Count']
                    else:
                        previous_index = list(repost_dict).index(statement_time) - 1
                        sub_query_str = ('Time == "Replace1" and modularity_class == "Replace2"'
                                         .replace('Replace1', list(repost_dict)[previous_index])
                                         .replace('Replace2', cluster))
                        increase_reposts = (df_subset['Count'].values[0] -
                                            interval_df.query(sub_query_str)['Count'].values[0])
                    repost_increase_df.loc[df_subset.index, 'Count'] = increase_reposts
                range_start_time += timedelta(hours=1)
                range_end_time += timedelta(hours=1)
            # リポスト推移（範囲内）
            print(Common.now() + '　　　　　csvを保存（リポスト推移（範囲内））', flush=True)
            interval_df.to_csv(k_kore_folder + '/リポスト推移（範囲内）.csv', encoding='utf-16')
            # リポスト推移（累計）
            print(Common.now() + '　　　　　csvを保存（リポスト推移（累計））', flush=True)
            total_df.to_csv(k_kore_folder + '/リポスト推移（累計）.csv', encoding='utf-16')
            # 感情スコア推移（範囲内）
            print(Common.now() + '　　　　　csvを保存（感情スコア推移（範囲内））', flush=True)
            # keyを行ラベル、valueを列ラベル
            sentimental_interval_df = pd.DataFrame.from_dict(sentimental_interval_dict, orient='index')
            sentimental_interval_df.columns = repost_rank_list
            sentimental_interval_df.to_csv(k_kore_folder + '/感情スコア推移（範囲内）.csv', encoding='utf-16')
            # 感情スコア推移（累計）
            print(Common.now() + '　　　　　csvを保存（感情スコア推移（累計））', flush=True)
            # keyを行ラベル、valueを列ラベル
            sentimental_total_df = pd.DataFrame.from_dict(sentimental_total_dict, orient='index')
            sentimental_total_df.columns = repost_rank_list
            sentimental_total_df.to_csv(k_kore_folder + '/感情スコア推移（累計）.csv', encoding='utf-16')
            # リポスト関係（範囲内）
            print(Common.now() + '　　　　　csvを保存（リポスト関係（範囲内））', flush=True)
            relation_interval_df.to_csv(k_kore_folder + '/リポスト関係（範囲内）.csv', encoding='utf-16')
            # リポスト関係（累計）
            print(Common.now() + '　　　　　csvを保存（リポスト関係（累計））', flush=True)
            relation_total_df.to_csv(k_kore_folder + '/リポスト関係（累計）.csv', encoding='utf-16')
            # クラスター係数推移
            print(Common.now() + '　　　　　csvを保存（クラスター係数推移）', flush=True)
            # keyを行ラベル、valueを列ラベル
            clustering_coefficient_df = pd.DataFrame.from_dict(clustering_coefficient_dict, orient='index')
            clustering_coefficient_df.columns = repost_rank_list
            clustering_coefficient_df.to_csv(k_kore_folder + '/クラスター係数推移.csv', encoding='utf-16')
            # リポスト件数推移
            print(Common.now() + '　　　　　csvを保存（リポスト件数推移）', flush=True)
            (pd.DataFrame.from_dict(repost_dict, orient='index')
             .to_csv(k_kore_folder + '/リポスト件数推移.csv', encoding='utf-16'))
            # リポスト件数推移（クラスター別）
            print(Common.now() + '　　　　　csvを保存（リポスト件数推移（クラスター別））', flush=True)
            # keyを行ラベル、valueを列ラベル
            repost_cluster_df = pd.DataFrame.from_dict(repost_cluster_dict, orient='index')
            repost_cluster_df.columns = repost_rank_list
            repost_cluster_df.to_csv(k_kore_folder + '/リポスト件数推移（クラスター別）.csv', encoding='utf-16')
            # リポスト増加件数推移
            print(Common.now() + '　　　　　csvを保存（リポスト増加件数推移）', flush=True)
            (pd.DataFrame.from_dict(repost_increase_dict, orient='index')
             .to_csv(k_kore_folder + '/リポスト増加件数推移.csv', encoding='utf-16'))
            # リポスト増加件数推移（クラスター別）
            print(Common.now() + '　　　　　csvを保存（リポスト増加件数推移（クラスター別））', flush=True)
            repost_increase_df.to_csv(k_kore_folder + '/リポスト増加件数推移（クラスター別）.csv', encoding='utf-16')
            # クラスター間リポスト関係（範囲内）
            print(Common.now() + '　　　　　csvを保存（クラスター間リポスト関係（範囲内））', flush=True)
            community_interval_df.to_csv(k_kore_folder + '/クラスター間リポスト関係（範囲内）.csv', encoding='utf-16')
            # クラスター間リポスト関係（累計）
            print(Common.now() + '　　　　　csvを保存（クラスター間リポスト関係（累計））', flush=True)
            community_total_df.to_csv(k_kore_folder + '/クラスター間リポスト関係（累計）.csv', encoding='utf-16')


if __name__ == '__main__':
    date_time()
