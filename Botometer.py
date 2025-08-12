import botometer
import tweepy
import sqlite3
import datetime
import configparser
import os
from csv import writer
import requests
import sys

word = sys.argv[1]


def main():

    twitter_main_path = os.getcwd() + ''

    # アカウントリスト（config）を読み込み
    conf = configparser.ConfigParser()
    config_file = twitter_main_path + '/アカウントリスト.ini'
    conf.read(config_file)

    use_key = ''

    # 現在時刻
    now = datetime.datetime.now()
    # アカウントDB登録
    conn = sqlite3.connect(twitter_main_path + '/db/' + word + 'Account.db')
    # カーソルオブジェクを作成
    cur = conn.cursor()

    # sqlite3.Error対応
    # requests.exceptions対応
    try:
        # チェック①
        # 24時間以内に使用するRapidApiKEYで更新を行ったアカウントが
        # 2,000件（余裕を持って1,950件以上）を超えている場合、終了
        cur.execute("SELECT * "
                    "FROM p_account "
                    "WHERE used_RapidApiKEY = ? AND "
                    "update_time >= ?",
                    (use_key, (now + datetime.timedelta(days=-1)).strftime('%Y/%m/%d %H:%M:%S')))
        # 24時間BOT判定上限数を超えている
        if len(cur.fetchall()) >= int(conf[str(use_key)]['limit']):
            print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                  '　24時間BOT判定上限数を超過（' + str(use_key) + '）',
                  flush=True)
        else:

            # チェック③
            # 「BOTスコア未設定」の最古アカウントを抽出し、アカウントが存在しない場合、終了
            non_updated_account = cur.execute("SELECT user_id, MIN(update_time) "
                                              "FROM p_account "
                                              "WHERE bot_score = '' AND "
                                              "used_RapidApiKEY = ?",
                                              (use_key, )).fetchall()
            # 「BOTスコア未設定」アカウントが存在しない
            if non_updated_account[0][0] is None:
                print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                      '　BOTスコア未設定アカウントなし（' + str(use_key) + '）',
                      flush=True)
                print('', flush=True)
            else:
                # 使用するRapidApiKEYの判定
                twitter_api = conf[str(use_key)]['twitter_api']
                # Botometerオブジェクト
                bom = botometer.Botometer(wait_on_ratelimit=True,
                                          rapidapi_key=conf[str(use_key)]['rapid_api_key'],
                                          consumer_key=conf[twitter_api]['api_key'],
                                          consumer_secret=conf[twitter_api]['api_secret'])
                # BOT判定
                update_user_id = non_updated_account[0][0]
                print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                      '　開始　　　used_RapidApiKEY（' + str(use_key) + '）',
                      flush=True)
                try:
                    # BOTスコア算出
                    """if update_user_id == 1585996988482469890 or update_user_id == 1279541322177708038:
                        pass
                    else:"""
                    result = bom.check_account(update_user_id)

                except tweepy.TweepError as e:
                    reason = e.reason
                    if "'code': 50, 'message': 'User not found.'" in reason:
                        score = 50
                    elif "'code': 63, 'message': 'User has been suspended.'" in reason:
                        score = 63
                    elif "'code': 34, 'message': 'Sorry, that page does not exist.'" in reason:
                        score = 34
                    elif "Not authorized." in reason:
                        score = 99
                    else:
                        score = 100
                    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                          '　チェック　used_RapidApiKEY（' + str(use_key) + '）、' + str(update_user_id) + '：' + reason,
                          flush=True)
                    # アカウントDB更新
                    cur.execute("UPDATE p_account "
                                "SET bot_score = ?, "
                                "update_time = ?, "
                                "cause = ?"
                                "WHERE user_id = ?",
                                (score,
                                 now.strftime('%Y/%m/%d %H:%M:%S'),
                                 reason,
                                 update_user_id))

                except botometer.NoTimelineError:
                    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                          '　チェック　used_RapidApiKEY（' + str(use_key) + '）、' + str(update_user_id) +
                          '：botometer.NoTimelineError',
                          flush=True)
                    # 一般アカウントDB更新
                    cur.execute("UPDATE p_account "
                                "SET bot_score = ?, "
                                "update_time = ?, "
                                "cause = ? "
                                "WHERE user_id = ?",
                                (999,
                                 now.strftime('%Y/%m/%d %H:%M:%S'),
                                 'botometer.NoTimelineError',
                                 update_user_id))
                else:
                    majority_lang = result['user']['majority_lang']

                    english_astroturf = result['raw_scores']['english']['astroturf']
                    english_fake_follower = result['raw_scores']['english']['fake_follower']
                    english_financial = result['raw_scores']['english']['financial']
                    english_other = result['raw_scores']['english']['other']
                    english_overall = result['raw_scores']['english']['overall']
                    english_self_declared = result['raw_scores']['english']['self_declared']
                    english_spammer = result['raw_scores']['english']['spammer']

                    universal_astroturf = result['raw_scores']['universal']['astroturf']
                    universal_fake_follower = result['raw_scores']['universal']['fake_follower']
                    universal_financial = result['raw_scores']['universal']['financial']
                    universal_other = result['raw_scores']['universal']['other']
                    universal_overall = result['raw_scores']['universal']['overall']
                    universal_self_declared = result['raw_scores']['universal']['self_declared']
                    universal_spammer = result['raw_scores']['universal']['spammer']
                    # アカウントDB更新
                    cur.execute("UPDATE p_account "
                                "SET bot_score = ?, "
                                "majority_lang = ?, "
                                "english_astroturf = ? , "
                                "english_fake_follower = ? , "
                                "english_financial = ? , "
                                "english_other = ? , "
                                "english_overall = ? , "
                                "english_self_declared = ? , "
                                "english_spammer = ? , "
                                "universal_astroturf = ? , "
                                "universal_fake_follower = ? , "
                                "universal_financial = ? , "
                                "universal_other = ? , "
                                "universal_overall = ? , "
                                "universal_self_declared = ? , "
                                "universal_spammer = ? , "
                                "update_time = ? , "
                                "cause = ? "
                                "WHERE user_id = ?",
                                (1,
                                 majority_lang,
                                 english_astroturf,
                                 english_fake_follower,
                                 english_financial,
                                 english_other,
                                 english_overall,
                                 english_self_declared,
                                 english_spammer,
                                 universal_astroturf,
                                 universal_fake_follower,
                                 universal_financial,
                                 universal_other,
                                 universal_overall,
                                 universal_self_declared,
                                 universal_spammer,
                                 now.strftime('%Y/%m/%d %H:%M:%S'),
                                 '',
                                 update_user_id),)
                # アカウントDB更新をコミット
                conn.commit()

                print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
                      '　正常終了　used_RapidApiKEY（' + str(use_key) + '）',
                      flush=True)
                print('', flush=True)

    # sqlite3.Error対応
    except sqlite3.Error as e:
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　異常終了　sqlite3.Error（' + str(use_key) + '）',
              flush=True)
        print('', flush=True)
        with open(twitter_main_path + '/csv/Exception_Log.csv', 'a', encoding='utf-16') as f:
            # csv writerオブジェクト
            writer_object = writer(f)
            # Exception発生日時、内容を追記
            writer_object.writerow(
                [datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                 'Account_Public.db(RapidAPI:' + str(use_key) + ')',
                 e.args[0]])
            # csvファイルクローズ
            f.close()

    # requests.exceptions対応
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException) as e:
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') +
              '　異常終了　requests.exceptions（' + str(use_key) + '）',
              flush=True)
        print('', flush=True)
        with open(twitter_main_path + '/csv/Exception_Log.csv', 'a', encoding='utf-16') as f:
            # csv writerオブジェクト
            writer_object = writer(f)
            # Exception発生日時、内容を追記
            writer_object.writerow(
                [datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                 'botometer_requests(RapidAPI:' + str(use_key) + ')',
                 e.args[0]])
            # csvファイルクローズ
            f.close()
    # アカウントDBクローズ
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
