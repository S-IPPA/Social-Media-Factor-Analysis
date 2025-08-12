import Analysis_Cluster
import Analysis_DateTime
import Analysis_Gephi
import Common
import FirstProcess
import Visualization_ClusterPercentage
import Visualization_ClusterRelationship
import Visualization_ClusterSentimental
import Visualization_DateTime
import Visualization_Repost_By_Bot
import Visualization_RepostPercentage_Bot
import glob
import os
import shutil

# データ収集ワード
WORD = 'PASCO コオロギ'
# データ収集開始日時
START_DATE = '2023/02/26 00:00:00'
# データ収集終了日時
END_DATE = '2023/03/23 23:59:59'
# データ重点分析終了日時
ANALYSIS_END_DATE = '2023/03/03 23:59:59'

# kコア分解上限
K_CORE_MAXIMUM = 5

# クラスター配色リスト
CLUSTER_COLOR = ['red', 'aqua', 'green',
                 'yellow', 'purple', 'blue',
                 'tomato', 'pink', 'teal',
                 'gold', 'violet', 'lime',
                 'brown', 'cyan', 'navy',
                 'coral', 'indigo', 'olive']

# カラーマップ辞書（クラスター色に応じたマップ、ワードクラウド用）
COLOR_MAP = {CLUSTER_COLOR[0]: 'autumn', CLUSTER_COLOR[1]: 'cool', CLUSTER_COLOR[2]: 'winter',
             CLUSTER_COLOR[3]: 'autumn', CLUSTER_COLOR[4]: 'cool', CLUSTER_COLOR[5]: 'winter',
             CLUSTER_COLOR[6]: 'autumn', CLUSTER_COLOR[7]: 'cool', CLUSTER_COLOR[8]: 'winter',
             CLUSTER_COLOR[9]: 'autumn', CLUSTER_COLOR[10]: 'cool', CLUSTER_COLOR[11]: 'winter',
             CLUSTER_COLOR[12]: 'autumn', CLUSTER_COLOR[13]: 'cool', CLUSTER_COLOR[14]: 'winter',
             CLUSTER_COLOR[15]: 'autumn', CLUSTER_COLOR[16]: 'cool', CLUSTER_COLOR[17]: 'winter'}

# ワードクラウド対象外ワード
DELETE_WORLD_LIST = ['PASCO', 'Pasco', 'ハ゜スコ', 'パスコ', 'コオロギ', 'コオロギ']

# csvフォルダパス
CSV_PATH = os.getcwd() + '/csv/' + WORD + '/'

# マスターcsv
MASTER_CSV = CSV_PATH + 'マスター.csv'

# リツイート先アカウントcsv
REPOSTED_ACCOUNT_CSV = CSV_PATH + 'リツイート先アカウント.csv'

# 統合フォルダパス
INTEGRATION_PATH = CSV_PATH + '統合/'
# kコア分解フォルダパス
K_CORE_I_PATH = INTEGRATION_PATH + 'kコア分解(n)/'

# ノードファイル名
FIRST_NODES_FILE_PATH = '/Gephi/' + FirstProcess.FIRST_NODES_FILE_NAME + '.csv'
# エッジファイル名
FIRST_EDGES_FILE_PATH = '/Gephi/' + FirstProcess.FIRST_EDGES_FILE_NAME + '.csv'

# 可視化フォルダパス
VISUALIZATION_PATH = CSV_PATH + '可視化/'
# kコア分解フォルダパス
K_CORE_V_PATH = VISUALIZATION_PATH + 'kコア分解(n)/'

# リポスト関係リスト
REPOST_RELATION = ['Bots repost Bots', 'Bots repost Humans', 'Humans repost Bots', 'Humans repost Humans']

# リポスト件数折れ線スタイル
Repost_Plot_Style = 'solid'
# エコーチェンバー折れ線スタイル
Echo_Plot_Style = 'dashed'
# 感情スコア折れ線スタイル
Sentimental_Plot_Style = 'dashdot'
# クラスター係数折れ線スタイル
Coefficient_Plot_Style = 'dotted'

# 時系列相互相関のラグ測定範囲（1日分 = 24時間）
MAX_LAG = 24

if __name__ == '__main__':
    # 初期処理（Gephiを用いた最初の可視化）が行われているか確認
    chk_flg = 0
    for k_kore_folder in Common.k_kore_folder_get():
        if (os.path.exists(k_kore_folder + FIRST_NODES_FILE_PATH) and
                os.path.exists(k_kore_folder + FIRST_EDGES_FILE_PATH)):
            chk_flg = 1
            break
    if chk_flg == 1:
        # 統合フォルダ整理（Gephi以外を削除）
        for k_kore_folder in Common.k_kore_folder_get():
            for folder_file_path in glob.glob(k_kore_folder + '/*'):
                # ファイル・フォルダ名を取得
                folder_file = folder_file_path.split('/')[-1]
                if folder_file != 'Gephi':
                    # ファイルを削除
                    if '.' in folder_file:
                        os.remove(folder_file_path)
                    # フォルダを削除
                    else:
                        shutil.rmtree(folder_file_path)
        # 可視化フォルダ作成
        if os.path.exists(VISUALIZATION_PATH):
            shutil.rmtree(VISUALIZATION_PATH)
        os.makedirs(VISUALIZATION_PATH)

        # 各クラスター処理
        Analysis_Cluster.cluster()
        # Gephi用GEXF作成
        Analysis_Gephi.gephi()
        # 時系列分析
        Analysis_DateTime.date_time()

        # クラスター割合図作成
        Visualization_ClusterPercentage.cluster_percentage()
        # 時系列可視化
        Visualization_DateTime.date_time(priority='')
        Visualization_DateTime.date_time(priority='（重点分析期間）')
        # クラスター相関関係ヒートマップ作成
        Visualization_ClusterRelationship.cluster_relationship()
        # リポスト割合ドーナツグラフ作成（ボット区別あり、kコア分解前後）
        Visualization_RepostPercentage_Bot.repost_percentage_bot()
        # ボットによるリポスト件数・割合棒グラフ作成（件数はcsvのみ）
        Visualization_Repost_By_Bot.repost_by_bot()
        # クラスター感情スコア箱ヒゲ図作成
        Visualization_ClusterSentimental.cluster_sentimental()

    else:
        print(Common.now() + '　初期処理（Gephiを用いた最初の可視化）未実施のため終了', flush=True)
