import Common
import csv
import datetime
import os
import requests
from time import sleep
import sys
from datetime import timedelta
import tweepy
from csv import writer
import configparser


# 検索ワード
query = sys.argv[1]
#query = 'PASCO コオロギ'
# ツイート収集期間
time_list = str(sys.argv[2]).split('-')
# ツイート収集開始年月日
start_year = time_list[0]
start_month = time_list[1]
start_day = time_list[2]
# ツイート収集終了年月日
end_year = time_list[3]
end_month = time_list[4]
end_day = time_list[5]
account = int(sys.argv[3])


def main():

    # ツイート件数カウンター
    i = 0
    # 新規ユーザーIDリスト（DBアクセス件数の省略化を目的）
    account_id_list = []
    # 新規ツイートIDリスト（再収集の際の重複回避用）
    tweet_id_list = []

    # 検索範囲日時指定（JSTからUTCに変換）
    start_time = datetime.datetime(int(start_year), int(start_month), int(start_day))
    start_time -= timedelta(hours=9)
    end_time = datetime.datetime(int(end_year), int(end_month), int(end_day))
    end_time += timedelta(hours=15)
    # アメリカ時間
    #start_time += timedelta(hours=14)
    #end_time -= timedelta(hours=10)

    # フォルダ新規作成
    dir_path = os.getcwd() + '/csv/' + query + '/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    # csvファイルパス
    csv_path = dir_path + start_year + start_month + start_day + '-' + end_year + end_month + end_day + query + '.csv'

    # アカウントリスト（config）を読み込み
    conf = configparser.ConfigParser()
    config_file = os.getcwd() + '/アカウントリスト.ini'
    conf.read(config_file)

    # 再収集（プログラム再起動）の場合（csvの存否で判定）
    if os.path.isfile(csv_path):
        with open(csv_path, encoding='utf-16') as f:
            reader = csv.reader(f)
            next(reader, None)
            for line in reader:
                i += 1
                # 収集済ツイートIDを設定
                tweet_id_list.append(line[0])
                # 収集済アカウントIDを設定
                if line[2] not in account_id_list:
                    account_id_list.append(line[2])
                if line[5] == 'RT' and line[6] not in account_id_list:
                    account_id_list.append(line[6])
                # 最終列ツイート日時を設定
                end_time = datetime.datetime.strptime(line[1], '%Y/%m/%d %H:%M:%S')
                end_time -= timedelta(hours=9)
                end_time += timedelta(seconds=1)
            f.close()

    # csvファイル作成
    with open(csv_path, 'a', encoding='utf-16') as f:
        # csv writerオブジェクト
        writer_object = writer(f)
        # csvファイル内タイトル設定（新規作成時）
        if os.path.getsize(csv_path) == 0:
            writer_object.writerow(['Tweet_Id',
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
                                    'Mention_Verified'])
        while True:
            # requests.exceptions対応
            try:
                # ツイート取得
                while True:
                    # tweepy.TweepyException対応
                    try:
                        tweets_list = tweepy.Paginator('',
                                                       query=query,
                                                       start_time=start_time,
                                                       end_time=end_time,
                                                       max_results=100)
                    except tweepy.TweepyException as te:
                        print(Common.now() + '　TweepyException1：' + str(te), flush=True)
                    else:
                        break
                for tweets in tweets_list:
                    if tweets is None:
                        break
                    for tweet in tweets[0]:
                        # ツイートID
                        tweet_id = str(tweet.id)
                        # 新規ツイートID判定（再収集の際の重複回避）
                        if tweet_id not in tweet_id_list:
                            i += 1

                            # 1,000ツイート毎にprint
                            if i % 1000 == 0:
                                print(Common.now() + '　' +
                                      start_year + start_month + start_day + '-' +
                                      end_year + end_month + end_day + '　' +
                                      query + '　' + str("{:,}".format(i)) + '件突破', flush=True)

                            # ツイート情報（statusオブジェクト）を取得
                            # ツイート正常取得フラグ
                            tweet_get_flg = 0
                            while True:
                                # tweepy.TweepyException対応
                                try:
                                    tweet_status = tweepy.API('', wait_on_rate_limit=True).get_status(id=tweet_id, tweet_mode='extended')
                                except tweepy.TweepyException as te:
                                    print(Common.now() + '　TweepyException2：' + str(te), flush=True)
                                    # ツイートが存在しない、権限がない場合、次のツイートへ
                                    if 'that page does not exist' in str(te) or \
                                            'No status found with that ID' in str(te) or \
                                            'Sorry, you are not authorized to see this status' in str(te):
                                        break
                                    pass
                                else:
                                    # ツイート正常取得フラグを設定
                                    tweet_get_flg = 1
                                    break
                            if tweet_get_flg == 1:
                                # 日時
                                tweet_status.created_at += timedelta(hours=9)
                                time = tweet_status.created_at.strftime('%Y/%m/%d %H:%M:%S')
                                # ユーザID
                                user_id = tweet_status.user.id_str
                                # カテゴリー
                                # リツイート先ユーザID
                                # リツイートユーザ名
                                # リツイートアカウント名
                                to_rt_user_id = ''
                                to_retweet_screen_name = ''
                                to_retweet_name = ''
                                if hasattr(tweet_status, 'retweeted_status'):
                                    category = 'RT'
                                    to_rt_user_id = tweet_status.retweeted_status.user.id_str
                                    to_retweet_screen_name = tweet_status.retweeted_status.user.screen_name
                                    to_retweet_name = tweet_status.retweeted_status.user.name
                                else:
                                    category = 'T'
                                # 本文
                                if category == 'RT':
                                    text = tweet_status.retweeted_status.full_text
                                else:
                                    text = tweet_status.full_text
                                # ハッシュタグ
                                hashtag = ''
                                if tweet_status.entities['hashtags']:
                                    for hashtags in tweet_status.entities['hashtags']:
                                        hashtag += hashtags['text'] + ','
                                # 記事元URL
                                article = ''
                                if tweet_status.entities['urls']:
                                    for articles in tweet_status.entities['urls']:
                                        article += articles['expanded_url'] + ','

                                # メンション
                                mention_ids = ''
                                mention_screen_name = ''
                                mention_followings = ''
                                mention_followers = ''
                                mention_verified = ''

                                # csvファイル追記
                                # 超例外的に、nameにNULL文字が入っていることがある
                                writer_object.writerow([tweet_id,
                                                        time,
                                                        user_id,
                                                        tweet_status.user.screen_name,
                                                        tweet_status.user.name.replace('\0', ''),
                                                        category,
                                                        to_rt_user_id,
                                                        to_retweet_screen_name,
                                                        to_retweet_name.replace('\0', ''),
                                                        text,
                                                        hashtag,
                                                        article,
                                                        mention_ids,
                                                        mention_screen_name,
                                                        mention_followings,
                                                        mention_followers,
                                                        mention_verified])

                                # 再収集を行う際に備えてend_timeを設定（UTCで）
                                end_time = datetime.datetime.strptime(time, '%Y/%m/%d %H:%M:%S')
                                end_time -= timedelta(hours=9)
                                end_time += timedelta(seconds=1)
                                # 再収集を行う際に備えて当該ツイートIDを追加（再収集の際はパス）
                                tweet_id_list.append(tweet_id)
            except (requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.RequestException) as r_e:

                # 1分待機
                sleep(60)
                Common.exception_log(file=start_year + start_month + start_day + '-' +
                                     end_year + end_month + end_day + query + '-' +
                                     str(tweet_id),
                                     error=r_e)
            else:
                # csvファイルクローズ
                f.close()
                break


if __name__ == '__main__':
    main()
