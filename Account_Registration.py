import Common
import csv
import glob
import os
import random
from time import sleep
import sqlite3
import sys
import tweepy

word = sys.argv[1]
#word = 'PASCO コオロギ'
account = int(sys.argv[2])

# 対象csvファイルリスト
file_list = glob.glob(os.getcwd() + '/csv/' + word + '/*.csv')
file_list = [f.replace(os.getcwd() + '/csv/' + word + '/', '') for f in file_list]


# アカウントDB登録
def account_db_registration(account_info_dict=None):
    dbname = os.getcwd() + '/db/' + word + 'Account.db'
    p_account_conn = sqlite3.connect(dbname)
    # カーソルオブジェクを作成
    p_account_cur = p_account_conn.cursor()
    # 登録完了までループ
    while True:
        # sqlite3.Error対応
        try:
            # テーブル作成
            p_account_cur.execute('CREATE TABLE IF NOT EXISTS p_account('
                                  'statuses_count INTEGER, '
                                  'user_id STRING, '
                                  'screen_name STRING, '
                                  'name STRING, '
                                  'profile_banner_url STRING, '
                                  'profile_image_url_https STRING, '
                                  'verified STRING, '
                                  'protected STRING, '
                                  'description STRING, '
                                  'location STRING, '
                                  'entities STRING, '
                                  'created_at STRING, '
                                  'friends_count INTEGER, '
                                  'followers_count INTEGER, '
                                  'registration_time STRING, '
                                  'majority_lang STRING, '
                                  'english_astroturf INTEGER, '
                                  'english_fake_follower INTEGER, '
                                  'english_financial INTEGER, '
                                  'english_other INTEGER, '
                                  'english_overall INTEGER, '
                                  'english_self_declared INTEGER, '
                                  'english_spammer INTEGER, '
                                  'universal_astroturf INTEGER, '
                                  'universal_fake_follower INTEGER, '
                                  'universal_financial INTEGER, '
                                  'universal_other INTEGER, '
                                  'universal_overall INTEGER, '
                                  'universal_self_declared INTEGER, '
                                  'universal_spammer INTEGER, '
                                  'bot_score INTEGER, '
                                  'used_RapidApiKEY INTEGER, '
                                  'update_time STRING, '
                                  'cause STRING, '
                                  'PRIMARY KEY(user_id))')
            # アカウントDB登録済チェック
            p_account_cur.execute("SELECT * FROM p_account WHERE user_id = ?", (account_info_dict['id_str'],))
            update_time = p_account_cur.fetchone()
            # 新規登録
            if update_time is None:
                # BOTスコア設定に用いるRapidApiKEYをランダム（1〜45）に設定
                p_account_cur.execute('INSERT INTO p_account('
                                      'statuses_count, '
                                      'user_id, '
                                      'screen_name, '
                                      'name, '
                                      'profile_banner_url , '
                                      'profile_image_url_https , '
                                      'verified, '
                                      'protected, '
                                      'description, '
                                      'location, '
                                      'entities, '
                                      'created_at, '
                                      'friends_count, '
                                      'followers_count, '
                                      'registration_time, '
                                      'majority_lang, '
                                      'english_astroturf, '
                                      'english_fake_follower, '
                                      'english_financial, '
                                      'english_other, '
                                      'english_overall, '
                                      'english_self_declared, '
                                      'english_spammer, '
                                      'universal_astroturf, '
                                      'universal_fake_follower, '
                                      'universal_financial, '
                                      'universal_other, '
                                      'universal_overall, '
                                      'universal_self_declared, '
                                      'universal_spammer, '
                                      'bot_score, '
                                      'used_RapidApiKEY, '
                                      'update_time, '
                                      'cause) '
                                      'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                                      (account_info_dict['statuses_count'],
                                       account_info_dict['id_str'],
                                       '@' + account_info_dict['screen_name'],
                                       account_info_dict['name'],
                                       account_info_dict['profile_banner_url'],
                                       account_info_dict['profile_image_url_https'],
                                       account_info_dict['verified'],
                                       account_info_dict['protected'],
                                       account_info_dict['description'],
                                       account_info_dict['location'],
                                       account_info_dict['entities'],
                                       account_info_dict['created_at'],
                                       account_info_dict['friends_count'],
                                       account_info_dict['followers_count'],
                                       account_info_dict['registration_time'],
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       '',
                                       random.randint(1, 45),
                                       Common.now(),
                                       ''))

            # アカウントDB更新をコミット
            p_account_conn.commit()
        except sqlite3.Error as se:
            Common.exception_log(file='Account_DB(Registration)', error=se.args[0])
        # 登録完了
        else:
            break
    # アカウントDBクローズ
    p_account_cur.close()
    p_account_conn.close()


# アカウント情報取得
def account_info_get(account_id='', account_count=0, target_file=''):
    account_count += 1
    # 進捗報告表示（100アカウント毎）
    if account_count % 100 == 0:
        print(Common.now() + '　アカウント登録' + str("{:,}".format(account_count)) + '件突破（' + target_file + '）',
              flush=True)

    # アカウント情報dict
    # ツイート数
    # ユーザID
    # ユーザ名
    # アカウント名
    # 背景画像
    # プロフィール画像
    # 認証
    # 鍵有無
    # 自己紹介文
    # 位置
    # URL
    # アカウント作成日時
    # フォロー数
    # フォロワー数
    account_info_dict = {'statuses_count': 0,
                         'id_str': account_id,
                         'screen_name': '',
                         'name': '',
                         'profile_banner_url': '',
                         'profile_image_url_https': '',
                         'verified': '',
                         'protected': '',
                         'description': '',
                         'location': '',
                         'entities': '',
                         'created_at': '',
                         'friends_count': 0,
                         'followers_count': 0,
                         'registration_time': Common.now()}

    # Exception発生件数カウンター（アカウント情報が取得出来るか不安）
    exception_count = 0
    while True:
        # tweepy.TweepyException対応
        try:
            auth = ''
            # アカウント情報取得
            user = tweepy.API(auth, wait_on_rate_limit=True).get_user(user_id=account_id)

            # アカウント情報dictへ設定
            account_info_dict['statuses_count'] = user.statuses_count
            account_info_dict['screen_name'] = user.screen_name
            account_info_dict['name'] = user.name
            if hasattr(user, 'profile_banner_url'):
                account_info_dict['profile_banner_url'] = user.profile_banner_url
            account_info_dict['profile_image_url_https'] = user.profile_image_url_https
            if user.verified:
                account_info_dict['verified'] = 'V'
            else:
                account_info_dict['verified'] = 'P'
            if user.protected:
                account_info_dict['protected'] = 'C'
            else:
                account_info_dict['protected'] = 'O'
            account_info_dict['description'] = user.description
            account_info_dict['location'] = user.location
            if 'url' in user.entities:
                if 'urls' in user.entities['url']:
                    if 'expanded_url' in user.entities['url']['urls'][0]:
                        account_info_dict['entities'] = user.entities['url']['urls'][0]['expanded_url']
            account_info_dict['created_at'] = user.created_at.strftime('%Y/%m/%d %H:%M:%S')
            account_info_dict['friends_count'] = user.friends_count
            account_info_dict['followers_count'] = user.followers_count

        except tweepy.TweepyException as t_e:
            exception_count += 1
            # 3回トライしてもNGの場合
            if exception_count == 3:
                print(Common.now() + '　アカウント情報取得異常：' + str(t_e),
                      flush=True)
                # ユーザIDのみDB登録
                account_db_registration(account_info_dict)
                return account_count
            # 1分待機
            sleep(60)

        else:
            break
    # アカウント情報DB登録
    account_db_registration(account_info_dict)
    return account_count


def main(file_name=''):
    # 新規登録アカウント件数カウンター
    account_count = 0
    # 新規ユーザーIDリスト（DBアクセス件数の省略化を目的）
    account_id_list = []

    # 一般アカウントDB
    dbname = os.getcwd() + '/db/' + word + 'Account.db'
    p_account_conn = sqlite3.connect(dbname)
    # カーソルオブジェクト作成
    p_account_cur = p_account_conn.cursor()
    # テーブル作成
    p_account_cur.execute('CREATE TABLE IF NOT EXISTS p_account('
                          'statuses_count INTEGER, '
                          'user_id STRING, '
                          'screen_name STRING, '
                          'name STRING, '
                          'profile_banner_url STRING, '
                          'profile_image_url_https STRING, '
                          'verified STRING, '
                          'protected STRING, '
                          'description STRING, '
                          'location STRING, '
                          'entities STRING, '
                          'created_at STRING, '
                          'friends_count INTEGER, '
                          'followers_count INTEGER, '
                          'registration_time STRING, '
                          'majority_lang STRING, '
                          'english_astroturf INTEGER, '
                          'english_fake_follower INTEGER, '
                          'english_financial INTEGER, '
                          'english_other INTEGER, '
                          'english_overall INTEGER, '
                          'english_self_declared INTEGER, '
                          'english_spammer INTEGER, '
                          'universal_astroturf INTEGER, '
                          'universal_fake_follower INTEGER, '
                          'universal_financial INTEGER, '
                          'universal_other INTEGER, '
                          'universal_overall INTEGER, '
                          'universal_self_declared INTEGER, '
                          'universal_spammer INTEGER, '
                          'bot_score INTEGER, '
                          'used_RapidApiKEY INTEGER, '
                          'update_time STRING, '
                          'cause STRING, '
                          'PRIMARY KEY(user_id))')
    # 取得完了までループ
    while True:
        # sqlite3.Error対応
        try:
            for record in p_account_cur.execute("SELECT user_id FROM p_account"):
                account_id_list.append(str(record[0]))
        except sqlite3.Error:
            pass
        # 登録完了
        else:
            break
    # 一般アカウントDBクローズ
    p_account_cur.close()
    p_account_conn.close()

    # 対象csvファイルオープン
    with open(os.getcwd() + '/csv/' + word + '/' + file_name, encoding='utf-16') as f:
        reader = csv.reader(f)
        next(reader, None)
        for line in reader:
            # ツイート・リツイートユーザID（新規判定）
            if line[2] not in account_id_list:
                # アカウント情報取得・DB登録
                account_count = account_info_get(account_id=line[2], account_count=account_count, target_file=file_name)
                account_id_list.append(line[2])
            # リツイート先ユーザID（新規判定）
            if line[5] == 'RT' and line[6] not in account_id_list:
                # アカウント情報取得・DB登録
                account_count = account_info_get(account_id=line[6], account_count=account_count, target_file=file_name)
                account_id_list.append(line[6])
    return account_count


if __name__ == '__main__':
    for file_count, file in enumerate(file_list, 1):
        try:
            print(Common.now() + '　アカウント登録開始　' + str(file_count) + '/' + str(len(file_list)) + '　(' + file + ')',
                  flush=True)
            count = main(file_name=file)
        # 異常終了
        except Exception as e:
            print(Common.now() + '　アカウント登録異常終了　' + str(file_count) + '/' + str(len(file_list)) + '　(' + file + ')',
                  flush=True)
            Common.exception_log(file='Registration(' + file + ')', error=e)
        # 正常終了
        else:
            print(Common.now() + '　アカウント登録正常終了　' + str(file_count) + '/' + str(len(file_list)) + '　(' + file + ')',
                  flush=True)
