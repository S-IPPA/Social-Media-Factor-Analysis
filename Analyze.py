import collections
from csv import writer
import datetime
from datetime import timedelta
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import shutil
import sqlite3

word = ''

# ワードクラウドにおいて対象外とするワード
delete_word_list = ['']

# csvフォルダパス
csv_path = os.getcwd() + '/csv/' + word + '/'

# 統合フォルダ
integration_dir_path = \
    csv_path + '統合/'
# 各統合csv
integration_folder = \
    integration_dir_path + '各統合csv/'
# ツイート退避フォルダ
integration_escape_folder = \
    integration_dir_path + 'ツイート退避/'
# ボットスコア記載済ツイートフォルダ
integration_tweet_folder = \
    integration_dir_path + 'ボットスコア記載済ツイート/'

# マスター統合csvファイル
integration_master = \
    integration_folder + 'マスター.csv'
# ツイートアカウント統合csvファイル
integration_tweet_account = \
    integration_folder + 'ツイートアカウント.csv'
# リツイートアカウント統合csvファイル
integration_retweet_account = \
    integration_folder + 'リツイートアカウント.csv'
# リツイート先アカウント統合csvファイル
integration_to_retweet_account = \
    integration_folder + 'リツイート先アカウント.csv'
# ハッシュタグリストcsvファイル
integration_hash_tag = \
    integration_folder + 'ハッシュタグ.csv'

# 可視化フォルダ
visualization_dir_path = csv_path + '可視化/'
# リツイート先アカウント分析フォルダ
visualization_to_retweet_folder = visualization_dir_path + 'リツイート先アカウント/'

# ボットスコア分布
visualization_bot_score = visualization_dir_path + 'ボットスコア分布.png'
# ツイートアカウント割合（アカウント別）
visualization_account_proportion = visualization_dir_path + 'ツイートアカウント割合（アカウント別）.png'
# ツイートアカウント割合（ツイート別）
visualization_tweet_proportion = visualization_dir_path + 'ツイートアカウント割合（ツイート別）.png'
# リツイート割合（ツイート別）
visualization_retweet_proportion = visualization_dir_path + 'リツイート割合（ツイート別）.png'
# リツイート割合（ソーシャルボット）
visualization_retweet_bot_proportion = visualization_dir_path + 'リツイート割合（ソーシャルボット）.png'
# 日別ツイート数
visualization_time = visualization_dir_path + '日別ツイート数.png'
# ツイートアカウト・リツイートアカウト相関（ヒートマップ）
visualization_heat_map = visualization_dir_path + 'ツイート・リツイート相関.png'
# ツイートアカウト・リツイートアカウト相関csvファイル（可視化フォルダ内に作成）
integration_heat_map = visualization_dir_path + 'ツイート・リツイート相関（参考）.csv'
# リツイート先アカウト情報設定有無（アカウント背景画像）
visualization_to_retweet_account_profile_banner_url = \
    visualization_to_retweet_folder + '【アカウント種別】アカウント背景画像.png'
# リツイート先アカウト情報設定有無（プロフィール画像）
visualization_to_retweet_account_profile_image_url_https = \
    visualization_to_retweet_folder + '【アカウント種別】プロフィール画像.png'
# リツイート先アカウト情報設定有無（自己紹介文）
visualization_to_retweet_account_description = visualization_to_retweet_folder + '【アカウント種別】自己紹介文.png'
# リツイート先アカウト情報設定有無（居住地）
visualization_to_retweet_account_location = visualization_to_retweet_folder + '【アカウント種別】居住地.png'
# リツイート先アカウト情報設定有無（URL）
visualization_to_retweet_account_entities = visualization_to_retweet_folder + '【アカウント種別】URL.png'
# リツイート先アカウト情報設定有無（認証）
visualization_to_retweet_account_verified = visualization_to_retweet_folder + '【アカウント種別】認証.png'
# リツイート先ソーシャルボット（認証アカウント）csvファイル（可視化フォルダ内に作成）
integration_to_retweet_account_verified_bot = visualization_to_retweet_folder + '【ソーシャルボット】認証アカウントリスト.csv'
# リツイート先アカウト情報（フォロー数）
visualization_to_retweet_account_friends = visualization_to_retweet_folder + '【アカウント種別】フォロー数.png'
# リツイート先アカウト情報（フォロー数）csvファイル（可視化フォルダ内に作成）
integration_to_retweet_account_friends = visualization_to_retweet_folder + '【アカウント種別】フォロー数（参考）.csv'
# リツイート先アカウト情報（フォロワー数）
visualization_to_retweet_account_followers = visualization_to_retweet_folder + '【アカウント種別】フォロワー数.png'
# リツイート先アカウト情報（フォロワー数）csvファイル（可視化フォルダ内に作成）
integration_to_retweet_account_followers = visualization_to_retweet_folder + '【アカウント種別】フォロワー数（参考）.csv'
# リツイート先ソーシャルボット（ナノインフルエンサー）csvファイル（可視化フォルダ内に作成）
integration_follower_nano = visualization_to_retweet_folder + '【ソーシャルボット】インフルエンサー（ナノ）.csv'
# リツイート先ソーシャルボット（マイクロインフルエンサー）csvファイル（可視化フォルダ内に作成）
integration_follower_micro = visualization_to_retweet_folder + '【ソーシャルボット】インフルエンサー（マイクロ）.csv'
# リツイート先ソーシャルボット（ミドルインフルエンサー）csvファイル（可視化フォルダ内に作成）
integration_follower_middle = visualization_to_retweet_folder + '【ソーシャルボット】インフルエンサー（ミドル）.csv'
# リツイート先ソーシャルボット（トップインフルエンサー）csvファイル（可視化フォルダ内に作成）
integration_follower_top = visualization_to_retweet_folder + '【ソーシャルボット】インフルエンサー（トップ）.csv'


# アカウント情報をDataFrameに記載
def account_df_make(account_df=None, account_id='', record_dict=None):
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Statuses_Count']] = record_dict['record_statuses_count']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Screen_Name']] = record_dict['record_screen_name']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Profile_Banner_url']] = record_dict['record_profile_banner_url']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Profile_Image_Url_Https']] = record_dict['record_profile_image_url_https']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Verified']] = record_dict['record_verified']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Protected']] = record_dict['record_protected']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Description']] = record_dict['record_description']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Location']] = record_dict['record_location']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Entities']] = record_dict['record_entities']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Created_At']] = record_dict['record_created_at']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Friends_Count']] = record_dict['record_friends_count']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Followers_Count']] = record_dict['record_followers_count']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Registration_Time']] = record_dict['record_registration_time']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Majority_Lang']] = record_dict['record_majority_lang']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['English_Astroturf']] = record_dict['record_english_astroturf']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['English_Fake_Follower']] = record_dict['record_english_fake_follower']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['English_Financial']] = record_dict['record_english_financial']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['English_Other']] = record_dict['record_english_other']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['English_Overall']] = record_dict['record_english_overall']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['English_Self_Declared']] = record_dict['record_english_self_declared']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['English_Spammer']] = record_dict['record_english_spammer']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Universal_Astroturf']] = record_dict['record_universal_astroturf']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Universal_Fake_Follower']] = record_dict['record_universal_fake_follower']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Universal_Financial']] = record_dict['record_universal_financial']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Universal_Other']] = record_dict['record_universal_other']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Universal_Overall']] = record_dict['record_universal_overall']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Universal_Self_Declared']] = record_dict['record_universal_self_declared']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Universal_Spammer']] = record_dict['record_universal_spammer']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Bot_Score']] = record_dict['record_bot_score']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Elapsed_Days']] = record_dict['record_elapsed_days']
    account_df.loc[account_df['User_Id'] == account_id,
                   ['Tweets_Per_Day']] = record_dict['record_tweets_per_day']
    return account_df


# 日別ツイート・リツイート数csvファイル作成
def tweet_retweet_time(time_list=None, path=''):
    time_dict = {}
    main_time_dict = {'年月日': [], 'ツイート数': []}
    # 同じ日付をカウント
    for t in time_list:
        d = datetime.datetime.strptime(t.split(' ')[0].replace('-', '/'), '%Y/%m/%d')
        if d in time_dict:
            time_dict[d] += 1
        else:
            time_dict[d] = 1
    for key in time_dict:
        main_time_dict['年月日'].append(key)
        main_time_dict['ツイート数'].append(time_dict[key])
    # DataFrame型に変換
    time_df = pd.DataFrame(data=main_time_dict)
    # 日付を昇順にソート
    time_df['年月日'] = pd.to_datetime(time_df['年月日'])
    time_df = time_df.sort_values(by='年月日', ascending=True)
    # csvファイル作成
    time_df.to_csv(path, encoding='utf-16', index=False)


# ツイート、アカウントにおける割合を算出、可視化
def proportion_visualization(score_list, visualization_file):
    bot_score_dict = {'Real User': 0,
                      'Bot User': 0,
                      'Unmeasurable': 0}
    for bot_score in score_list:
        if bot_score < 0.5:
            bot_score_dict['Real User'] += 1
        elif 0.5 <= bot_score <= 1:
            bot_score_dict['Bot User'] += 1
        else:
            bot_score_dict['Unmeasurable'] += 1
    # DataFrame型に変換
    bot_score_df = pd.DataFrame({'label': list(bot_score_dict.keys()),
                                 'value': list(bot_score_dict.values())})
    # 枠線の太さを3、線の色を白
    plt.pie(bot_score_df['value'],
            labels=['Real User\n' + str("{:,}".format(bot_score_dict['Real User'])) + ' Accounts',
                    'Bot User\n' + str("{:,}".format(bot_score_dict['Bot User'])) + ' Accounts',
                    'Unmeasurable\n' + str("{:,}".format(bot_score_dict['Unmeasurable'])) + ' Accounts'],
            textprops={'size': 'large'},
            autopct='%1.1f%%',
            colors=['deepskyblue', 'mediumseagreen', 'red'],
            startangle=90,
            counterclock=False,
            wedgeprops={'linewidth': 3, 'edgecolor': "white"})
    plt.savefig(visualization_file)
    plt.close('all')


# ヒートマップ用csvにおけるインデックスを設定
def heat_map_index(score=None):
    index = 0
    if score < 0.05:
        pass
    elif 0.05 <= score < 0.1:
        index = 1
    elif 0.1 <= score < 0.15:
        index = 2
    elif 0.15 <= score < 0.2:
        index = 3
    elif 0.2 <= score < 0.25:
        index = 4
    elif 0.25 <= score < 0.3:
        index = 5
    elif 0.3 <= score < 0.35:
        index = 6
    elif 0.35 <= score < 0.4:
        index = 7
    elif 0.4 <= score < 0.45:
        index = 8
    elif 0.45 <= score < 0.5:
        index = 9
    elif 0.5 <= score < 0.55:
        index = 10
    elif 0.55 <= score < 0.6:
        index = 11
    elif 0.6 <= score < 0.65:
        index = 12
    elif 0.65 <= score < 0.7:
        index = 13
    elif 0.7 <= score < 0.75:
        index = 14
    elif 0.75 <= score < 0.8:
        index = 15
    elif 0.8 <= score < 0.85:
        index = 16
    elif 0.85 <= score < 0.9:
        index = 17
    elif 0.9 <= score < 0.95:
        index = 18
    elif 0.95 <= score:
        index = 19
    return index


def account_setting_visualization(item='', criterion='', path=''):
    account_type_list = ['全アカウント', '人間', 'ソーシャルボット']
    for account_type in account_type_list:
        category_dict = {'Yes': 0, 'No': 0}
        # リツイート先アカウント統合csvファイルをDataFrame型で読み込み
        df = pd.read_csv(integration_to_retweet_account, dtype=object, encoding='utf-16')
        # リツイート先アカウントを全行読み込み
        for index, row in df.iterrows():
            bot_score = round(float(row['Bot_Score']), 2)
            category = row[item]
            # 後続の処理に備え、「Verified」（認証）が「P」（一般）のものはブランクを設定
            if item == 'Verified' and category == 'P':
                category = ''
            if account_type == '全アカウント' and 0 <= bot_score <= 1:
                if type(category) is str and \
                        category is not None and \
                        category != criterion:
                    category_dict['Yes'] += 1
                else:
                    category_dict['No'] += 1
            elif account_type == '人間' and bot_score < 0.5:
                if type(category) is str and \
                        category is not None and \
                        category != criterion:
                    category_dict['Yes'] += 1
                else:
                    category_dict['No'] += 1
            elif account_type == 'ソーシャルボット' and 0.5 <= bot_score <= 1:
                if type(category) is str and \
                        category is not None and \
                        category != criterion:
                    category_dict['Yes'] += 1
                else:
                    category_dict['No'] += 1
        # DataFrame型に変換
        category_df = pd.DataFrame({'label': list(category_dict.keys()),
                                    'value': list(category_dict.values())})
        # 枠線の太さを3、線の色を白
        plt.pie(category_df['value'],
                labels=['Yes\n' + str("{:,}".format(category_dict['Yes'])) + ' Accounts',
                        'No\n' + str("{:,}".format(category_dict['No'])) + ' Accounts'],
                autopct='%1.1f%%',
                colors=['lightcoral', 'khaki'],
                startangle=90,
                counterclock=False,
                wedgeprops={'linewidth': 3, 'edgecolor': "white"})
        plt.savefig(path.replace('【アカウント種別】',
                                 '【' + account_type + '】'))
        plt.close('all')

        # ソーシャルボットの場合、認証アカウント一覧を作成
        if account_type == 'ソーシャルボット' and item == 'Verified':
            with open(integration_to_retweet_account_verified_bot, 'a', encoding='utf-16') as f:
                writer_object = writer(f)
                writer_object.writerow(['フォロワー数', 'ユーザ名', '自己紹介文'])
                # リツイート先アカウントを全行読み込み
                for index, row in df.iterrows():
                    category = row[item]
                    bot_score = round(float(row['Bot_Score']), 2)
                    screen_name = row['Screen_Name']
                    description = row['Description']
                    if 0.5 <= bot_score <= 1 and category == 'V':
                        writer_object.writerow([screen_name, description])
                f.close()


def account_setting_visualization_friends(item='', visualization_path='', integration_path=''):
    account_type_list = ['全アカウント', '人間', 'ソーシャルボット']
    for account_type in account_type_list:
        category_dict = {'1万未満': 0, '1万以上': 0, '10万以上': 0, '100万以上': 0}
        # リツイート先アカウント統合csvファイルをDataFrame型で読み込み
        df = pd.read_csv(integration_to_retweet_account, dtype=object, encoding='utf-16')
        # リツイート先アカウントを全行読み込み
        for index, row in df.iterrows():
            bot_score = round(float(row['Bot_Score']), 2)
            category = int(row[item])
            if account_type == '全アカウント' and 0 <= bot_score <= 1:
                if category < 10000:
                    category_dict['1万未満'] += 1
                elif 10000 <= category < 100000:
                    category_dict['1万以上'] += 1
                elif 100000 <= category < 1000000:
                    category_dict['10万以上'] += 1
                elif 1000000 <= category:
                    category_dict['100万以上'] += 1
            elif account_type == '人間' and bot_score < 0.5:
                if category < 10000:
                    category_dict['1万未満'] += 1
                elif 10000 <= category < 100000:
                    category_dict['1万以上'] += 1
                elif 100000 <= category < 1000000:
                    category_dict['10万以上'] += 1
                elif 1000000 <= category:
                    category_dict['100万以上'] += 1
            elif account_type == 'ソーシャルボット' and 0.5 <= bot_score <= 1:
                if category < 10000:
                    category_dict['1万未満'] += 1
                elif 10000 <= category < 100000:
                    category_dict['1万以上'] += 1
                elif 100000 <= category < 1000000:
                    category_dict['10万以上'] += 1
                elif 1000000 <= category:
                    category_dict['100万以上'] += 1
        # DataFrame型に変換
        category_df = pd.DataFrame({'label': list(category_dict.keys()),
                                    'value': list(category_dict.values())})
        # 枠線の太さを3、線の色を白
        plt.pie(category_df['value'],
                labels=['1万未満\n' + str("{:,}".format(category_dict['1万未満'])) + ' Accounts',
                        '1万以上\n' + str("{:,}".format(category_dict['1万以上'])) + ' Accounts',
                        '10万以上\n' + str("{:,}".format(category_dict['10万以上'])) + ' Accounts',
                        '100万以上\n' + str("{:,}".format(category_dict['100万以上'])) + ' Accounts'],
                autopct='%1.1f%%',
                colors=['lightyellow', 'lightgreen', 'lightskyblue', 'lightpink'],
                startangle=90,
                counterclock=False,
                wedgeprops={'linewidth': 3, 'edgecolor': "white"})
        plt.savefig(
            visualization_path.replace('【アカウント種別】',
                                       '【' + account_type + '】'))
        category_df.to_csv(
            integration_path.replace('【アカウント種別】',
                                     '【' + account_type + '】'))
        plt.close('all')

        # ソーシャルボットの場合、フォロワーのカテゴリー毎に一覧を作成
        if account_type == 'ソーシャルボット' and item == 'Followers_Count':
            # フォロワー数の降順にソート
            df[item] = df[item].astype('int')
            followers_df = df.sort_values(by=item, ascending=False)
            # csvファイル先頭ラベル
            label = ['フォロワー数', 'ユーザ名']
            # ナノインフルエンサー（フォロワー数：1万未満）
            with open(integration_follower_nano, 'a', encoding='utf-16') as follower_nano_f:
                writer_object_nano = writer(follower_nano_f)
                writer_object_nano.writerow(label)
                # マイクロインフルエンサー（フォロワー数：1万以上）
                with open(integration_follower_micro, 'a', encoding='utf-16') as follower_micro_f:
                    writer_object_micro = writer(follower_micro_f)
                    writer_object_micro.writerow(label)
                    # ミドルインフルエンサー（フォロワー数：10万以上）
                    with open(integration_follower_middle, 'a', encoding='utf-16') as follower_middle_f:
                        writer_object_middle = writer(follower_middle_f)
                        writer_object_middle.writerow(label)
                        # トップインフルエンサー（フォロワー数：100万以上）
                        with open(integration_follower_top, 'a', encoding='utf-16') as follower_top_f:
                            writer_object_top = writer(follower_top_f)
                            writer_object_top.writerow(label)

                            # リツイート先アカウントを全行読み込み
                            for index, row in followers_df.iterrows():
                                bot_score = round(float(row['Bot_Score']), 2)
                                followers = int(row[item])
                                screen_name = row['Screen_Name']
                                if 0.5 <= bot_score <= 1:
                                    if followers < 10000:
                                        writer_object_nano.writerow([followers, screen_name])
                                    elif 10000 <= followers < 100000:
                                        writer_object_micro.writerow([followers, screen_name])
                                    elif 100000 <= followers < 1000000:
                                        writer_object_middle.writerow([followers, screen_name])
                                    elif 1000000 <= followers:
                                        writer_object_top.writerow([followers, screen_name])
                            follower_top_f.close()
                        follower_middle_f.close()
                    follower_micro_f.close()
                follower_nano_f.close()


# 可視化ボットスコア分布（カーネル密度推定）
def bot_score_distribution():
    bot_score_list = pd.read_csv(integration_tweet_account, dtype=object, encoding='utf-16')['Bot_Score'].tolist()
    new_bot_score_list = []
    for bot_score_str in bot_score_list:
        bot_score = float(bot_score_str)
        if bot_score <= 1:
            new_bot_score_list.append(bot_score)
    bot_score_df = pd.DataFrame(data=new_bot_score_list, columns=['Bot_Score'])
    sns.kdeplot(bot_score_df['Bot_Score'])
    plt.savefig(visualization_bot_score)
    plt.close('all')


# 可視化ツイートアカウント割合（アカウント別）（円グラフ）
def account_proportion():
    bot_score_list = []
    account_id_list = []
    df = pd.read_csv(integration_master, dtype=object, encoding='utf-16')
    sub_account_id_list = df['User_Id'].tolist()
    for i, account_id in enumerate(sub_account_id_list, 1):
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              'ツイート情報(' + str("{:,}".format(i)) + '/' +
              str("{:,}".format(len(sub_account_id_list))) + '件目)',
              flush=True)
        if account_id not in account_id_list:
            account_id_list.append(account_id)
    import sqlite3
    conn = sqlite3.connect(os.getcwd() + '/db/' + word + 'Account.db')
    cur = conn.cursor()
    for i, account_id in enumerate(account_id_list, 1):
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              'アカウント情報(' + str("{:,}".format(i)) + '/' +
              str("{:,}".format(len(account_id_list))) + '件目)',
              flush=True)
        record = cur.execute("SELECT statuses_count, "
                             "user_id, "
                             "screen_name, "
                             "name, "
                             "profile_banner_url, "
                             "profile_image_url_https, "
                             "verified, "
                             "protected, "
                             "description, "
                             "location, "
                             "entities, "
                             "created_at, "
                             "friends_count, "
                             "followers_count, "
                             "registration_time, "
                             "majority_lang, "
                             "english_astroturf, "
                             "english_fake_follower, "
                             "english_financial, "
                             "english_other, "
                             "english_overall, "
                             "english_self_declared, "
                             "english_spammer, "
                             "universal_astroturf, "
                             "universal_fake_follower, "
                             "universal_financial, "
                             "universal_other, "
                             "universal_overall, "
                             "universal_self_declared, "
                             "universal_spammer, "
                             "bot_score "
                             "FROM p_account "
                             "WHERE user_id = ?",
                             (account_id,)).fetchall()[0]
        record_dict = {'record_statuses_count': record[0],
                       'record_user_id': record[1],
                       'record_screen_name': record[2],
                       'record_name': record[3],
                       'record_profile_banner_url': record[4],
                       'record_profile_image_url_https': record[5],
                       'record_verified': record[6],
                       'record_protected': record[7],
                       'record_description':
                           str(record[8]).replace('\0', '').replace('\r\n', ' ').replace('\r', ' ').replace('\n',
                                                                                                            ' '),
                       'record_location': record[9],
                       'record_entities': record[10],
                       'record_created_at': record[11],
                       'record_friends_count': record[12],
                       'record_followers_count': record[13],
                       'record_registration_time': record[14],
                       'record_majority_lang': record[15],
                       'record_english_astroturf': record[16],
                       'record_english_fake_follower': record[17],
                       'record_english_financial': record[18],
                       'record_english_other': record[19],
                       'record_english_overall': record[20],
                       'record_english_self_declared': record[21],
                       'record_english_spammer': record[22],
                       'record_universal_astroturf': record[23],
                       'record_universal_fake_follower': record[24],
                       'record_universal_financial': record[25],
                       'record_universal_other': record[26],
                       'record_universal_overall': record[27],
                       'record_universal_self_declared': record[28],
                       'record_universal_spammer': record[29],
                       'record_bot_score': record[30]}
        # ボットスコアが1以下（正常に登録されている場合）
        if record_dict['record_bot_score'] <= 1:
            # 英語の場合、englishスコア
            if record_dict['record_majority_lang'] == 'en':
                record_dict['record_bot_score'] = record_dict['record_english_overall']
            # 英語以外の場合、universalスコア
            else:
                record_dict['record_bot_score'] = record_dict['record_universal_overall']
        bot_score_list.append(round(float(record_dict['record_bot_score']), 2))

    proportion_visualization(bot_score_list, visualization_account_proportion)


# 可視化ツイートアカウント割合（全ツイート）（円グラフ）
def tweet_proportion():
    all_bot_score_list = []
    for all_bot_score in pd.read_csv(integration_master, dtype=object, encoding='utf-16')['Bot_Score'].tolist():
        all_bot_score_list.append(round(float(all_bot_score), 2))
    proportion_visualization(all_bot_score_list, visualization_tweet_proportion)


# 可視化リツイート割合（全ツイート）（円グラフ）
def retweet_proportion():
    category_dict = {'ReTweet': 0, 'Tweet': 0}
    for category in pd.read_csv(integration_master, dtype=object, encoding='utf-16')['Category'].tolist():
        if category == 'RT':
            category_dict['ReTweet'] += 1
        else:
            category_dict['Tweet'] += 1
    # DataFrame型に変換
    category_df = pd.DataFrame({'label': list(category_dict.keys()),
                                'value': list(category_dict.values())})
    # 枠線の太さを3、線の色を白
    plt.pie(category_df['value'],
            labels=['ReTweet\n' + str("{:,}".format(category_dict['ReTweet'])),
                    'Others\n' + str("{:,}".format(category_dict['Tweet']))],
            textprops={'size': 'large'},
            autopct='%1.1f%%',
            colors=['lightcoral', 'khaki'],
            startangle=90,
            counterclock=False,
            wedgeprops={'linewidth': 3, 'edgecolor': "white"})
    plt.savefig(visualization_retweet_proportion)
    plt.close('all')


# 可視化リツイート割合（全ツイート）（円グラフ）
def retweet_bot_proportion():
    category_dict = {'ReTweet': 0, 'Tweet': 0}
    # マスター統合csvファイルをDataFrame型で読み込み
    df = pd.read_csv(integration_master, dtype=object, encoding='utf-16')
    # ツイートを全行読み込み
    for index, row in df.iterrows():
        bot_score = round(float(row['Bot_Score']), 2)
        category = row['Category']
        if 0.5 <= bot_score <= 1:
            if category == 'RT':
                category_dict['ReTweet'] += 1
            else:
                category_dict['Tweet'] += 1
    # DataFrame型に変換
    category_df = pd.DataFrame({'label': list(category_dict.keys()),
                                'value': list(category_dict.values())})
    # 枠線の太さを3、線の色を白
    plt.pie(category_df['value'],
            labels=['ReTweet\n' + str("{:,}".format(category_dict['ReTweet'])),
                    'Others\n' + str("{:,}".format(category_dict['Tweet']))],
            textprops={'size': 'large'},
            autopct='%1.1f%%',
            colors=['lightcoral', 'khaki'],
            startangle=90,
            counterclock=False,
            wedgeprops={'linewidth': 3, 'edgecolor': "white"})
    plt.savefig(visualization_retweet_bot_proportion)
    plt.close('all')


# 可視化ツイートアカウト・リツイートアカウト相関（ヒートマップ）
def heat_map():
    # ヒートマップ用DataFrameを定義（20*20, int）
    hm_df = pd.DataFrame(np.asarray(np.zeros([20, 20]), dtype=int))
    # マスター統合csvファイルをDataFrame型で読み込み
    df = pd.read_csv(integration_master, dtype=object, encoding='utf-16')
    # リツイートのDataFrameを順次読み込み
    for index, row in df.loc[df['Category'] == 'RT', ['Bot_Score', 'To_ReTweet_Bot_Score']].iterrows():
        # ツイートアカウント及びリツイート先アカウント共にボットスコアが正しく設定されている場合
        if float(row['Bot_Score']) <= 1 and float(row['To_ReTweet_Bot_Score']) <= 1:
            hm_df.loc[heat_map_index(float(row['Bot_Score'])), heat_map_index(float(row['To_ReTweet_Bot_Score']))] += 1
    # 行を降順にソート
    hm_df = hm_df.sort_index(ascending=False)
    # 0.1毎にラベルを記載
    for i in range(20):
        if i == 0:
            hm_df = hm_df.rename(columns={i: '0'}, index={i: '0'})
        elif i % 2 == 0:
            label = str(i / 20)
            hm_df = hm_df.rename(columns={i: label}, index={i: label})
        else:
            hm_df = hm_df.rename(columns={i: ''}, index={i: ''})
    hm_df.to_csv(integration_heat_map)
    ax = sns.heatmap(hm_df, cmap='CMRmap_r', cbar_kws={'label': 'Retweets'}, linewidths=.1, linecolor='Gray')
    ax.set_xlabel('Bot score of retweeter')
    ax.set_ylabel('Bot score of tweeter')
    # Y軸の目盛を水平に記載
    plt.yticks(rotation='horizontal')
    plt.savefig(visualization_heat_map)
    plt.close('all')


# 統合メイン処理
def integration():
    # 各統合csvフォルダ作成
    if os.path.exists(integration_folder):
        shutil.rmtree(integration_folder)
    os.makedirs(integration_folder)
    # ツイート退避フォルダ作成（既存の場合はパス）
    if not os.path.exists(integration_escape_folder):
        os.makedirs(integration_escape_folder)
    # ボットスコア記載済ツイートフォルダ作成（既存の場合はパス）
    if not os.path.exists(integration_tweet_folder):
        os.makedirs(integration_tweet_folder)

    # 対象csvファイル読込
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　1/18　対象全csvファイル読込開始', flush=True)
    csv_list = glob.glob(csv_path + '*.csv')
    for csv_count, csv_file in enumerate(csv_list, 1):
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　    　対象csvファイル　' + str(csv_count) + '/' + str(len(csv_list)) +
              '　(' + csv_file.split(csv_path)[1] + ')読込開始',
              flush=True)
        # アカウントIDリスト
        account_id_list = []
        # 対象csvファイルをDataFrame型で読み込み
        df = pd.read_csv(csv_file, dtype=object, encoding='utf-16')
        sub_df = df.loc[df['Category'] == 'RT']
        # 列名を設定
        df.columns = ['Tweet_Id',
                      'Time',
                      'User_Id',
                      'Screen_Name',
                      'Name',
                      'Category',
                      'To_ReTweet',
                      'To_ReTweet_Screen_Name',
                      'To_ReTweet_Name',
                      'Text',
                      'HashTag',
                      'Article',
                      'Mention_User_Id',
                      'Mention_Screen_Name',
                      'Mention_Followings',
                      'Mention_Followers',
                      'Mention_Verified']
        # ボットスコア及び認証を記載する列を追加
        df.insert(5, 'Bot_Score', 0)
        df.insert(6, 'Verified', '')
        df.insert(11, 'To_ReTweet_Bot_Score', 0)
        df.insert(12, 'To_ReTweet_Verified', '')
        # メンション関連を削除
        del df['Mention_User_Id']
        del df['Mention_Screen_Name']
        del df['Mention_Followings']
        del df['Mention_Followers']
        del df['Mention_Verified']
        # アカウント名、リツイートアカウント名、ツイート文のNULL、改行を置換
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　    　対象csvファイル　' + str(csv_count) + '/' + str(len(csv_list)) +
              '　1/4　アカウント名、リツイートアカウント名、ツイート文のNULL、改行を置換',
              flush=True)
        i = 0
        lines = len(df['Tweet_Id'].tolist())
        for index, row in df.iterrows():
            i += 1
            if i % 1000 == 0:
                print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                      '　    　　　   　　　　　   　   　進捗状況：' + str("{:,}".format(i)) + '/' + str("{:,}".format(lines)) + '行',
                      flush=True)
            if type(row['Category']) is str and row['Category'] is not None and row['Category'] != '':
                # アカウント名
                name = row['Name']
                if type(name) is str and name is not None and name != '':
                    df.loc[df['Tweet_Id'] == row['Tweet_Id'], ['Name']] = \
                        name.replace('\0', '').replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
                # リツイートアカウント名
                to_retweet_name = row['To_ReTweet_Name']
                if type(to_retweet_name) is str and to_retweet_name is not None and to_retweet_name != '':
                    df.loc[df['Tweet_Id'] == row['Tweet_Id'], ['To_ReTweet_Name']] = \
                        to_retweet_name.replace('\0', '').replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
                # ツイート文
                text = row['Text']
                if type(text) is str and text is not None and text != '':
                    df.loc[df['Tweet_Id'] == row['Tweet_Id'], ['Text']] = \
                        text.replace('\0', '').replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
            else:
                print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　    　　　   　　　　　   　   　　空白行のため要確認', flush=True)

            # 海外の場合、時差調整
            time_set = datetime.datetime.strptime(row['Time'], '%Y/%m/%d %H:%M:%S')
            time_set -= timedelta(hours=14)
            df.loc[df['Tweet_Id'] == row['Tweet_Id'], ['Time']] = time_set

        # ツイートアカウントIDを全取得
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　    　対象csvファイル　' + str(csv_count) + '/' + str(len(csv_list)) +
              '　2/4　ツイートアカウントIDを全取得',
              flush=True)
        for account_id in df['User_Id'].tolist():
            if account_id not in account_id_list:
                account_id_list.append(account_id)
        # リツイート先アカウントIDを全取得
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　    　対象csvファイル　' + str(csv_count) + '/' + str(len(csv_list)) +
              '　3/4　リツイート先アカウントIDを全取得',
              flush=True)
        for account_id in sub_df['To_ReTweet'].tolist():
            if account_id not in account_id_list:
                account_id_list.append(account_id)
        # アカウントDBをオープン
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　    　対象csvファイル　' + str(csv_count) + '/' + str(len(csv_list)) +
              '　4/4　アカウントIDに紐付くアカウント情報' + str("{:,}".format(len(account_id_list))) + '件をDBから全取得',
              flush=True)
        conn = sqlite3.connect(os.getcwd() + '/db/' + word + 'Account.db')
        cur = conn.cursor()
        for i, account_id in enumerate(account_id_list, 1):
            if i % 1000 == 0:
                print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                      '　    　　　   　　　　　   　   　アカウント情報をDataFrameに記載中(' + str("{:,}".format(i)) + '/' +
                      str("{:,}".format(len(account_id_list))) + ')',
                      flush=True)
            # アカウントIDに紐付くアカウント情報を取得
            record = cur.execute("SELECT verified, "
                                 "majority_lang, "
                                 "english_overall, "
                                 "universal_overall, "
                                 "bot_score "
                                 "FROM p_account "
                                 "WHERE user_id = ?",
                                 (account_id,)).fetchall()[0]
            bot_score = record[4]
            # ボットスコアが1以下（正常に登録されている場合）
            if bot_score <= 1:
                # 英語の場合、englishスコア
                if record[1] == 'en':
                    bot_score = record[2]
                # 英語以外の場合、universalスコア
                else:
                    bot_score = record[3]
            # ツイートアカウントのボットスコア及び認証を記載
            df.loc[df['User_Id'] == account_id, ['Bot_Score']] = bot_score
            df.loc[df['User_Id'] == account_id, ['Verified']] = record[0]
            # リツイート先アカウントのボットスコア及び認証を記載
            df.loc[df['To_ReTweet'] == account_id, ['To_ReTweet_Bot_Score']] = bot_score
            df.loc[df['To_ReTweet'] == account_id, ['To_ReTweet_Verified']] = record[0]
        # アカウントDBをクローズ
        cur.close()
        conn.close()
        # ボットスコア記載済ツイートフォルダに保存
        df.to_csv(integration_tweet_folder + csv_file.split(csv_path)[1], encoding='utf-16')
        # 既存のツイートファイルはツイート退避フォルダに移動
        shutil.move(csv_file, integration_escape_folder + csv_file.split(csv_path)[1])

    # マスター統合csvファイル作成
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　2/18　マスター統合csvファイル作成開始', flush=True)
    # 対象csvファイルの内容を追加（マスター統合csvファイル作成）
    data_list = []
    # 新規ツイート判定リスト
    tweet_id_list = []
    csv_list = glob.glob(integration_tweet_folder + '*.csv')
    for csv_count, csv_file in enumerate(csv_list, 1):
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　    　対象csvファイル　' + str(csv_count) + '/' + str(len(csv_list)) +
              '　(' + csv_file.split(csv_path)[1] + ')読込・追加開始',
              flush=True)
        # 対象csvファイルをDataFrame型で読み込み
        df = pd.read_csv(csv_file, dtype=object, encoding='utf-16')
        # ツイート重複判定
        id_list = df['Tweet_Id'].tolist()
        for tweet_id in id_list:
            if tweet_id in tweet_id_list:
                print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　    　　ツイート重複あり：' + str(tweet_id), flush=True)
                line = id_list.index(tweet_id)
                df.drop(df.index[[line]])
            else:
                tweet_id_list.append(tweet_id)
        data_list.append(df)
    pd.concat(data_list).to_csv(integration_master, encoding='utf-16')

    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　3/18　マスター統合csvファイル読込開始', flush=True)
    df = pd.read_csv(integration_master, dtype=object, encoding='utf-16')

    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　4/18　マスター統合csvファイルからリツイート抽出開始', flush=True)
    sub_df = df.loc[df['Category'] == 'RT']

    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　5/18　ツイートアカウント、リツイートアカウント、リツイート先アカウントDataFrame作成開始', flush=True)
    # アカウントIDリスト
    account_id_list = []
    # 共通DataFrameカラム
    master_columns = ['Statuses_Count',
                      'User_Id',
                      'Screen_Name',
                      'Profile_Banner_url',
                      'Profile_Image_Url_Https',
                      'Verified',
                      'Protected',
                      'Description',
                      'Location',
                      'Entities',
                      'Created_At',
                      'Friends_Count',
                      'Followers_Count',
                      'Registration_Time',
                      'Majority_Lang',
                      'English_Astroturf',
                      'English_Fake_Follower',
                      'English_Financial',
                      'English_Other',
                      'English_Overall',
                      'English_Self_Declared',
                      'English_Spammer',
                      'Universal_Astroturf',
                      'Universal_Fake_Follower',
                      'Universal_Financial',
                      'Universal_Other',
                      'Universal_Overall',
                      'Universal_Self_Declared',
                      'Universal_Spammer',
                      'Bot_Score',
                      'Count',
                      'Elapsed_Days',
                      'Tweets_Per_Day']
    # ツイートアカウントDataFrame
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　    　ツイートアカウントDataFrame作成開始', flush=True)
    tweet_account_df = pd.DataFrame(data=None, columns=master_columns)
    i = 0
    sub_account_id_list = df['User_Id'].tolist()
    for account_id in sub_account_id_list:
        i += 1
        if i % 1000 == 0:
            print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                  '　    　　進捗状況：' + str("{:,}".format(i)) + '/' + str("{:,}".format(len(sub_account_id_list))) + '件',
                  flush=True)
        if account_id in tweet_account_df['User_Id'].tolist():
            tweet_account_df.loc[tweet_account_df['User_Id'] == account_id, ['Count']] += 1
        else:
            df_append = pd.DataFrame(data=[[0, account_id, '', '', '', '', '', '', '', '', '', 0, 0, '',
                                            '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]],
                                     columns=master_columns)
            tweet_account_df = pd.concat([tweet_account_df, df_append])
        if account_id not in account_id_list:
            account_id_list.append(account_id)
    # リツイートアカウントDataFrame
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　    　リツイートアカウントDataFrame作成開始', flush=True)
    retweet_account_df = pd.DataFrame(data=None, columns=master_columns)
    i = 0
    sub_account_id_list = sub_df['User_Id'].tolist()
    for account_id in sub_account_id_list:
        i += 1
        if i % 1000 == 0:
            print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                  '　    　　進捗状況：' + str("{:,}".format(i)) + '/' + str("{:,}".format(len(sub_account_id_list))) + '件',
                  flush=True)
        if account_id in retweet_account_df['User_Id'].tolist():
            retweet_account_df.loc[retweet_account_df['User_Id'] == account_id, ['Count']] += 1
        else:
            df_append = pd.DataFrame(data=[[0, account_id, '', '', '', '', '', '', '', '', '', 0, 0, '',
                                            '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]],
                                     columns=master_columns)
            retweet_account_df = pd.concat([retweet_account_df, df_append])
    # リツイート先アカウントDataFrame
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　    　リツイート先アカウントDataFrame作成開始', flush=True)
    to_retweet_account_df = pd.DataFrame(data=None, columns=master_columns)
    i = 0
    sub_account_id_list = sub_df['To_ReTweet'].tolist()
    for account_id in sub_account_id_list:
        i += 1
        if i % 1000 == 0:
            print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                  '　    　　進捗状況：' + str("{:,}".format(i)) + '/' + str("{:,}".format(len(sub_account_id_list))) + '件',
                  flush=True)
        if account_id in to_retweet_account_df['User_Id'].tolist():
            to_retweet_account_df.loc[to_retweet_account_df['User_Id'] == account_id, ['Count']] += 1
        else:
            df_append = pd.DataFrame(data=[[0, account_id, '', '', '', '', '', '', '', '', '', 0, 0, '',
                                            '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]],
                                     columns=master_columns)
            to_retweet_account_df = pd.concat([to_retweet_account_df, df_append], axis=0)
        if account_id not in account_id_list:
            account_id_list.append(account_id)
    # アカウントDBをオープン
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　    　アカウント情報をDBから読み込み各DataFrameに記載', flush=True)
    conn = sqlite3.connect(os.getcwd() + '/db/' + word + 'Account.db')
    cur = conn.cursor()
    for i, account_id in enumerate(account_id_list, 1):
        if i % 1000 == 0:
            print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                  '　    　　アカウント情報を各DataFrameに記載中(' + str("{:,}".format(i)) + '/' +
                  str("{:,}".format(len(account_id_list))) + ')',
                  flush=True)
        # アカウントIDに紐付くアカウント情報を取得
        record = cur.execute("SELECT statuses_count, "
                             "user_id, "
                             "screen_name, "
                             "name, "
                             "profile_banner_url, "
                             "profile_image_url_https, "
                             "verified, "
                             "protected, "
                             "description, "
                             "location, "
                             "entities, "
                             "created_at, "
                             "friends_count, "
                             "followers_count, "
                             "registration_time, "
                             "majority_lang, "
                             "english_astroturf, "
                             "english_fake_follower, "
                             "english_financial, "
                             "english_other, "
                             "english_overall, "
                             "english_self_declared, "
                             "english_spammer, "
                             "universal_astroturf, "
                             "universal_fake_follower, "
                             "universal_financial, "
                             "universal_other, "
                             "universal_overall, "
                             "universal_self_declared, "
                             "universal_spammer, "
                             "bot_score "
                             "FROM p_account "
                             "WHERE user_id = ?",
                             (account_id,)).fetchall()[0]
        # アカウント活動期間（アカウント作成から本分析にあたってのDB登録までの日数）を計算
        elapsed_days = 0
        if record[11] != '':
            elapsed_days = (datetime.datetime.strptime(record[14].replace('-', '/'), '%Y/%m/%d %H:%M:%S') -
                            datetime.datetime.strptime(record[11].replace('-', '/'), '%Y/%m/%d %H:%M:%S')).days
        # 1日当たりのツイート数を計算
        if elapsed_days == 0:
            elapsed_days = 1
        tweets_per_day = record[0] // elapsed_days
        # アカウント情報を設定
        record_dict = {'record_statuses_count': record[0],
                       'record_user_id': record[1],
                       'record_screen_name': record[2],
                       'record_name': record[3],
                       'record_profile_banner_url': record[4],
                       'record_profile_image_url_https': record[5],
                       'record_verified': record[6],
                       'record_protected': record[7],
                       'record_description':
                           str(record[8]).replace('\0', '').replace('\r\n', ' ').replace('\r', ' ').replace('\n',
                                                                                                            ' '),
                       'record_location': record[9],
                       'record_entities': record[10],
                       'record_created_at': record[11],
                       'record_friends_count': record[12],
                       'record_followers_count': record[13],
                       'record_registration_time': record[14],
                       'record_majority_lang': record[15],
                       'record_english_astroturf': record[16],
                       'record_english_fake_follower': record[17],
                       'record_english_financial': record[18],
                       'record_english_other': record[19],
                       'record_english_overall': record[20],
                       'record_english_self_declared': record[21],
                       'record_english_spammer': record[22],
                       'record_universal_astroturf': record[23],
                       'record_universal_fake_follower': record[24],
                       'record_universal_financial': record[25],
                       'record_universal_other': record[26],
                       'record_universal_overall': record[27],
                       'record_universal_self_declared': record[28],
                       'record_universal_spammer': record[29],
                       'record_bot_score': record[30],
                       'record_elapsed_days': elapsed_days,
                       'record_tweets_per_day': tweets_per_day}
        # ボットスコアが1以下（正常に登録されている場合）
        if record_dict['record_bot_score'] <= 1:
            # 英語の場合、englishスコア
            if record_dict['record_majority_lang'] == 'en':
                record_dict['record_bot_score'] = record_dict['record_english_overall']
            # 英語以外の場合、universalスコア
            else:
                record_dict['record_bot_score'] = record_dict['record_universal_overall']
        # ツイートアカウントDataFrameに記載
        if account_id in tweet_account_df['User_Id'].tolist():
            tweet_account_df = account_df_make(tweet_account_df, account_id, record_dict)
        # リツイートアカウントDataFrameに記載
        if account_id in retweet_account_df['User_Id'].tolist():
            retweet_account_df = account_df_make(retweet_account_df, account_id, record_dict)
        # リツイート先アカウントDataFrameに記載
        if account_id in to_retweet_account_df['User_Id'].tolist():
            to_retweet_account_df = account_df_make(to_retweet_account_df, account_id, record_dict)

    # ツイートアカウントcsvファイル作成
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　6/18　ツイート先アカウント統合csvファイル作成開始', flush=True)
    tweet_account_df.to_csv(integration_tweet_account, encoding='utf-16')

    # リツイートアカウントcsvファイル作成
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　7/18　リツイートアカウント統合csvファイル作成開始', flush=True)
    retweet_account_df.to_csv(integration_retweet_account, encoding='utf-16')

    # リツイート先アカウントcsvファイル作成
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　8/18　リツイート先アカウント統合csvファイル作成開始', flush=True)
    to_retweet_account_df.to_csv(integration_to_retweet_account, encoding='utf-16')

    # ハッシュタグランキングcsvファイル作成
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　9/18　ハッシュタグリストcsvファイル作成開始', flush=True)
    # ハッシュタグリスト
    hashtag_list = []
    i = 0
    hashtag_line_list = df['HashTag'].tolist()
    for hashtag in hashtag_line_list:
        i += 1
        if i % 1000 == 0:
            print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                  '　    　　進捗状況：' + str("{:,}".format(i)) + '/' + str("{:,}".format(len(hashtag_line_list))) + '件',
                  flush=True)
        # float型の非数・nan対策
        if type(hashtag) is str and \
                hashtag is not None and \
                hashtag != '':
            hashtag_list += str(hashtag).split(',')
            # 追加したハッシュタグリスト内のブランクを削除
            if '' in hashtag_list:
                hashtag_list.remove('')
    with open(integration_hash_tag, 'a', encoding='utf-16') as hash_tag_f:
        # csv writerオブジェクト
        writer_object = writer(hash_tag_f)
        writer_object.writerow(['ハッシュタグ', '回数'])
        for hash_tag in collections.Counter(hashtag_list).most_common():
            # csvファイルに記載
            writer_object.writerow([hash_tag[0], hash_tag[1]])
        hash_tag_f.close()


if __name__ == '__main__':
    # 統合処理
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　統合処理開始', flush=True)
    integration()
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　統合処理完了', flush=True)

    # 可視化処理
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　可視化処理開始', flush=True)
    # 可視化フォルダ新規作成
    if os.path.exists(visualization_dir_path):
        shutil.rmtree(visualization_dir_path)
    os.makedirs(visualization_to_retweet_folder)
    # ボットスコア分布（カーネル密度推定）
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　①ボットスコア分布描写開始', flush=True)
    bot_score_distribution()
    # ツイートアカウント割合（アカウント別）（円グラフ）
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　②ツイートアカウント割合（アカウント別）描写開始', flush=True)
    account_proportion()
    # ツイートアカウント割合（全ツイート）（円グラフ）
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　③ツイートアカウント割合（全ツイート）描写開始', flush=True)
    tweet_proportion()
    # リツイート割合（全ツイート）（円グラフ）
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　④リツイート割合（全ツイート）描写開始', flush=True)
    retweet_proportion()
    # リツイート割合（ソーシャルボット）（円グラフ）
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　⑤リツイート割合（ソーシャルボット）描写開始', flush=True)
    retweet_bot_proportion()
    # 日別ツイート数（折れ線グラフ）
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　⑥日別ツイート数描写開始', flush=True)
    # ツイートアカウト・リツイートアカウト相関（ヒートマップ）
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '　⑦ツイートアカウト・リツイートアカウト相関（ヒートマップ）描写開始', flush=True)
    heat_map()
