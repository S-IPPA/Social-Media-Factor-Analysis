from csv import writer
import Main
from janome.tokenizer import Tokenizer
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy
import os
import re
import seaborn as sns
import wordcloud


# 折れ線グラフの色が黄色の場合、色を濃いめに変更
def yellow_line(color=''):
    if color == 'yellow':
        return 'gold'
    else:
        return color


# 円グラフ描写（凡例なし）
def pie_chart_v(title='', x=None, labels=None, colors=None, file=''):
    plt.pie(x=x['value'],
            labels=labels,
            textprops={'size': 'large'},
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            counterclock=False,
            wedgeprops={'linewidth': 3, 'edgecolor': "white"})
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 円グラフ描写（凡例あり）
def pie_chart_legend_v(title='', x=None, labels=None, colors=None, file=''):
    # ラベルは凡例で表示
    plt.pie(x=x,
            colors=colors,
            startangle=90,
            counterclock=False,
            wedgeprops={'linewidth': 1, 'edgecolor': "white"})
    # 凡例設定
    plt.legend(labels,
               fontsize=11,
               bbox_to_anchor=(0.9, 1.1))
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 棒グラフ描写
def bar_v(title='', df=None, x_ticks=None, repost_rank_list=None,  file=''):
    ax = df.plot.bar(stacked=True,
                     color=repost_rank_list,
                     legend=False)
    # X軸の目盛りラベル設定（0時台のみ日にちを記載）
    x_tick_labels = []
    for item in ax.get_xticklabels():
        time = x_ticks[int(item.get_text()) - 1]
        if '00時' in time:
            x_tick_labels.append(time.replace(' 00時', ''))
        else:
            x_tick_labels.append('')
    ax.set_xticklabels(x_tick_labels)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# エリアチャート描写
def area_v(title='', df=None, color=None, file=''):
    ax = df.plot.area(color=color, figsize=(12, 6))
    ax.set_xticks(numpy.arange(1, len(df.index.tolist()) + 1))
    # X軸の目盛りラベル設定（0時台のみ日にちを記載）
    x_tick_labels = []
    for time in df.index.values:
        if '00時' in time:
            x_tick_labels.append(time.replace(' 00時', ''))
        else:
            x_tick_labels.append('')
    ax.set_xticklabels(x_tick_labels)
    # X軸の目盛り非表示
    ax.tick_params(bottom=False)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.xticks(rotation=90)
    plt.xticks(fontsize=9)
    plt.xlabel('')
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 折れ線グラフ描写
def line_v(title='', df=None, linestyle='', x_ticks=None, repost_rank_list=None,
           file='', lw=0, legend=None, invert_yaxis=False):
    ax = df.plot(linestyle=linestyle, color=repost_rank_list, linewidth=lw, figsize=(12, 6))
    ax.set_xticks(numpy.arange(1, len(x_ticks)+1))
    # X軸の目盛りラベル設定（0時台のみ日にちを記載）
    x_tick_labels = []
    for x_tick in x_ticks:
        if '00時' in x_tick:
            x_tick_labels.append(x_tick.replace(' 00時', ''))
        else:
            x_tick_labels.append('')
    ax.set_xticklabels(x_tick_labels)
    # X軸の目盛り非表示
    ax.tick_params(bottom=False)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    # Y軸を反転させる
    if invert_yaxis:
        plt.gca().invert_yaxis()
    # 凡例非表示
    if not legend:
        ax.get_legend().remove()
    sns.set(style='white')
    plt.xticks(rotation=90)
    plt.xticks(fontsize=9)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# ネットワーク図描写
def network_v(title='', g=None, node_color=None, pos=None, cmap=None, file=''):
    # カラーマップ不使用
    if cmap == '':
        nx.draw_networkx(g,
                         node_color=node_color,
                         pos=pos,
                         node_size=1,
                         with_labels=False,
                         edge_color='lightgray')
    # カラーマップ使用
    else:
        nx.draw_networkx(g,
                         node_color=node_color,
                         pos=pos,
                         cmap=cmap,
                         node_size=1,
                         with_labels=False,
                         edge_color='lightgray')
    # 枠線を非表示
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# ワードクラウド描写
def wordcloud_v(title='', colormap='', text_list=None, file=''):
    text = ''
    for tweet_text in text_list:
        # URLを抽出し削除
        urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', tweet_text)
        for url in urls:
            tweet_text = tweet_text.replace(url, '')
        # 対象外ワードを抽出し削除
        for delete_word in Main.DELETE_WORLD_LIST:
            tweet_text = tweet_text.replace(delete_word, '')
        text = text + ' ' + tweet_text
    word_list = []
    # 単語リスト作成
    for token in Tokenizer().tokenize(text):
        if token.part_of_speech.split(',')[0] == '名詞':
            word_list.append(token.surface)
    # ワードクラウド描写
    wc = wordcloud.WordCloud(width=1000,
                             height=600,
                             min_font_size=15,
                             background_color='white',
                             font_path=os.getcwd() + '/font/MEIRYO.TTC',
                             regexp=r'[\w"]+',
                             colormap=colormap)
    wc.generate(' '.join(word_list))
    plt.imshow(wc)
    # 枠線を非表示
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    # 軸のラベルを非表示
    plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)
    plt.title(title)
    plt.savefig(file + 'wordcloud.png')
    plt.clf()
    plt.close('all')


# ヒートマップ描写
def heatmap_v(title='', df=None, bar=None, x_label='', y_label='', file=''):
    plt.subplots(figsize=(9, 7))
    sns.heatmap(df,
                cmap='CMRmap_r',
                cbar_kws=bar,
                linewidths=.1,
                linecolor='Gray')
    # ラベル文字
    plt.xlabel(x_label, fontsize=10)
    plt.ylabel(y_label, fontsize=10)
    # 目盛文字サイズ
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 散布図描写
def scatter_v(title='', data=None, palette=None, x='', y='', hue='', file=''):
    plt.subplots(figsize=(11, 8))
    sns.scatterplot(x=x,
                    y=y,
                    hue=hue,
                    s=200,
                    data=data,
                    palette=palette)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 2軸グラフ描写
def double_plot_v(title='', connection_df=None, time_list=None, linestyle1='',linestyle2='',
                  line_color='', bar_color='', line_columns='', bar_columns='',  ax1_y_label='',
                  ax2_y_label='', invert_yaxis1=False, invert_yaxis2=False, file=''):
    # プロットの作成
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    # 2軸グラフの本体設定
    ax1.plot(time_list, connection_df[line_columns], linestyle=linestyle1, color=yellow_line(color=line_color), label=line_columns)
    ax2.plot(time_list, connection_df[bar_columns], linestyle=linestyle2, color=yellow_line(color=bar_color), label=bar_columns)
    # 目盛線ラベルのフォントサイズ
    plt.tick_params(labelsize=10)
    # 凡例の表示のため、handler1と2にはグラフオブジェクトのリスト情報を設定
    # label1と2には、凡例用に各labelのリスト情報を設定
    handler1, label1 = ax1.get_legend_handles_labels()
    handler2, label2 = ax2.get_legend_handles_labels()
    # 凡例をまとめて出力する
    ax1.legend(handler1 + handler2, label1 + label2, loc="lower center", bbox_to_anchor=(.5, 1.1), ncol=3)
    # X軸の目盛り非表示
    ax1.tick_params(bottom=False)
    ax2.tick_params(bottom=False)
    # Y軸のラベル表示
    ax1.set_ylabel(ax1_y_label)
    ax2.set_ylabel(ax2_y_label)
    # Y軸を反転させる
    if invert_yaxis1:
        ax1.invert_yaxis()
    if invert_yaxis2:
        ax2.invert_yaxis()
    # X軸の目盛りラベル初期設定
    ax1.set_xticks(numpy.arange(1, len(time_list) + 1))
    # X軸の目盛りラベル設定（0時台のみ日にちを記載）
    x_tick_labels = []
    for x_tick in time_list:
        if '00時' in x_tick:
            x_tick_labels.append(x_tick.replace(' 00時', ''))
        else:
            x_tick_labels.append('')
    ax1.xaxis.set_tick_params(rotation=90)
    ax1.set_xticklabels(x_tick_labels)
    ax2.axes.xaxis.set_visible(False)
    plt.title(title)
    plt.savefig(file, bbox_inches='tight')
    plt.clf()
    plt.close('all')


# 2軸グラフ描写（エリアチャート + 折れ線グラフ）
def double_area_v(title='', area_df=None, plot_list=None, linestyle='', time_list=None, color_list=None,
                  plot_label='', ax1_y_label='', ax2_y_label='', invert_yaxis=False, file=''):
    # プロットの作成
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    # 日時の重複を削除
    unique_list = []
    [unique_list.append(x) for x in time_list if x not in unique_list]
    # 各層のエリアを設定
    y1 = numpy.array(area_df[Main.REPOST_RELATION[0]])
    y2 = y1 + numpy.array(area_df[Main.REPOST_RELATION[1]])
    y3 = y2 + numpy.array(area_df[Main.REPOST_RELATION[2]])
    y4 = y3 + numpy.array(area_df[Main.REPOST_RELATION[3]])
    # エリアチャートの描画
    ax1.fill_between(x=unique_list,
                     y1=y1,
                     color=color_list[0],
                     label=Main.REPOST_RELATION[0])
    ax1.fill_between(x=unique_list,
                     y1=y1,
                     y2=y2,
                     color=color_list[1],
                     label=Main.REPOST_RELATION[1])
    ax1.fill_between(x=unique_list,
                     y1=y2,
                     y2=y3,
                     color=color_list[2],
                     label=Main.REPOST_RELATION[2])
    ax1.fill_between(x=unique_list,
                     y1=y3,
                     y2=y4,
                     color=color_list[3],
                     label=Main.REPOST_RELATION[3])
    # 折れ線グラフの描画
    if title == '':
        ax2.plot(unique_list, plot_list, linestyle=linestyle, color='black', label=plot_label)
    else:
        ax2.plot(unique_list, plot_list, linestyle=linestyle, color=yellow_line(color=title), label=plot_label)
    # 目盛線ラベルのフォントサイズ
    plt.tick_params(labelsize=10)
    # 凡例の表示のため、handler1と2にはグラフオブジェクトのリスト情報を設定
    # label1と2には、凡例用に各labelのリスト情報を設定
    handler1, label1 = ax1.get_legend_handles_labels()
    handler2, label2 = ax2.get_legend_handles_labels()
    # 凡例をまとめて出力する
    ax1.legend(handler1 + handler2, label1 + label2, loc="lower center", bbox_to_anchor=(.5, 1.1), ncol=3)
    # X軸の目盛り非表示
    ax1.tick_params(bottom=False)
    ax2.tick_params(bottom=False)
    # Y軸のラベル表示
    ax1.set_ylabel(ax1_y_label)
    ax2.set_ylabel(ax2_y_label)
    # Y軸を反転させる
    if invert_yaxis:
        ax2.invert_yaxis()
    # X軸の目盛りラベル初期設定
    ax1.set_xticks(numpy.arange(1, len(unique_list)+1))
    # X軸の目盛りラベル設定（0時台のみ日にちを記載）
    x_tick_labels = []
    for x_tick in unique_list:
        if '00時' in x_tick:
            x_tick_labels.append(x_tick.replace(' 00時', ''))
        else:
            x_tick_labels.append('')
    ax1.xaxis.set_tick_params(rotation=90)
    ax1.set_xticklabels(x_tick_labels)
    ax2.axes.xaxis.set_visible(False)
    plt.title(title)
    plt.savefig(file, bbox_inches='tight')
    plt.clf()
    plt.close('all')


# 4軸グラフ描写（エリアチャート + 折れ線グラフ3種類）
def quartet_v(title='', area_df=None,
              plot_list1=None, linestyle1='', plot_label1='', linecolor1='', linewidth1=0,
              plot_list2=None, linestyle2='', plot_label2='', linecolor2='', linewidth2=0,
              plot_list3=None, linestyle3='', plot_label3='', linecolor3='', linewidth3=0,
              ax1_y_label='', ax2_y_label='', ax3_y_label='', ax4_y_label='',
              time_list=None, color_list=None, invert_yaxis=False, file=''):
    # プロットの作成
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax4 = ax1.twinx()
    # 日時の重複を削除
    unique_list = []
    [unique_list.append(x) for x in time_list if x not in unique_list]
    # 各層のエリアを設定
    y1 = numpy.array(area_df[Main.REPOST_RELATION[0]])
    y2 = y1 + numpy.array(area_df[Main.REPOST_RELATION[1]])
    y3 = y2 + numpy.array(area_df[Main.REPOST_RELATION[2]])
    y4 = y3 + numpy.array(area_df[Main.REPOST_RELATION[3]])
    # エリアチャートの描画
    ax1.fill_between(x=unique_list,
                     y1=y1,
                     color=color_list[0],
                     label=Main.REPOST_RELATION[0])
    ax1.fill_between(x=unique_list,
                     y1=y1,
                     y2=y2,
                     color=color_list[1],
                     label=Main.REPOST_RELATION[1])
    ax1.fill_between(x=unique_list,
                     y1=y2,
                     y2=y3,
                     color=color_list[2],
                     label=Main.REPOST_RELATION[2])
    ax1.fill_between(x=unique_list,
                     y1=y3,
                     y2=y4,
                     color=color_list[3],
                     label=Main.REPOST_RELATION[3])
    # 折れ線グラフの描画（1つ目）
    ax2.plot(unique_list, plot_list1, linestyle=linestyle1, color=yellow_line(color=linecolor1), label=plot_label1, linewidth=linewidth1)
    # 折れ線グラフの描画（2つ目）
    ax3.plot(unique_list, plot_list2, linestyle=linestyle2, color=yellow_line(color=linecolor2), label=plot_label2, linewidth=linewidth2)
    # 折れ線グラフの描画（3つ目）
    ax4.plot(unique_list, plot_list3, linestyle=linestyle3, color=yellow_line(color=linecolor3), label=plot_label3, linewidth=linewidth3)
    # 目盛線ラベルのフォントサイズ
    plt.tick_params(labelsize=10)
    # 凡例の表示のため、グラフオブジェクトのリスト情報を設定
    # l例用に各labelのリスト情報を設定
    handler1, label1 = ax1.get_legend_handles_labels()
    handler2, label2 = ax2.get_legend_handles_labels()
    handler3, label3 = ax3.get_legend_handles_labels()
    handler4, label4 = ax4.get_legend_handles_labels()
    # 凡例をまとめて出力する
    ax1.legend(handler1 + handler2 + handler3 + handler4,
               label1 + label2 + label3 + label4,
               loc="lower center", bbox_to_anchor=(.5, 1.1), ncol=4)
    # X軸の目盛り非表示
    ax1.tick_params(bottom=False)
    ax2.tick_params(bottom=False)
    ax3.tick_params(bottom=False)
    ax4.tick_params(bottom=False)
    # Y軸のラベル表示
    ax1.set_ylabel(ax1_y_label)
    ax2.set_ylabel(ax2_y_label)
    ax3.set_ylabel(ax3_y_label)
    ax3.yaxis.set_label_position('left')
    ax3.spines['left'].set_position(('axes', -0.15))
    ax3.yaxis.tick_left()
    ax4.set_ylabel(ax4_y_label)
    ax4.spines['right'].set_position(('axes', 1.15))
    # Y軸を反転させる
    if invert_yaxis:
        ax3.invert_yaxis()
    # X軸の目盛りラベル初期設定
    ax1.set_xticks(numpy.arange(1, len(unique_list)+1))
    # X軸の目盛りラベル設定（0時台のみ日にちを記載）
    x_tick_labels = []
    for x_tick in unique_list:
        if '00時' in x_tick:
            x_tick_labels.append(x_tick.replace(' 00時', ''))
        else:
            x_tick_labels.append('')
    ax1.xaxis.set_tick_params(rotation=90)
    ax1.set_xticklabels(x_tick_labels)
    ax2.axes.xaxis.set_visible(False)
    ax3.axes.xaxis.set_visible(False)
    ax4.axes.xaxis.set_visible(False)
    plt.title(title)
    plt.savefig(file, bbox_inches='tight')
    plt.clf()
    plt.close('all')


# ドーナツグラフ描写
def single_doughnut_v(title='',
                      main_list=None, main_labels=None, main_colors=None,
                      legend=None, category=None, bbox_to_anchor=None,
                      file=''):
    wedgeprops = {"width": 0.8, "edgecolor": 'white'}
    # ドーナツグラフ作成
    plt.rcParams['font.family'] = 'Arial Unicode MS'
    plt.pie(x=main_list, labels=main_labels, startangle=90, counterclock=False, labeldistance=0.8, colors=main_colors,
            wedgeprops=wedgeprops)
    # 凡例設定
    plt.legend(legend, fontsize=12, bbox_to_anchor=bbox_to_anchor)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')

    # csvにて保存（各件数について）
    file = file.replace('.png', '.csv')
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'a', encoding='utf-16') as f:
        writer_object = writer(f)
        writer_object.writerow(['No', 'Category', 'Count'])
        for row in legend:
            writer_object.writerow([row,
                                    category[legend.index(row)],
                                    main_list[legend.index(row)]])
        f.close()


# 2重ドーナツグラフ描写
def double_doughnut_v(title='',
                      main_list=None, sub_list=None,
                      main_labels=None, sub_labels=None,
                      main_colors=None, sub_colors=None,
                      legend=None, category=None, bbox_to_anchor=None,
                      file=''):
    wedgeprops = {"width": 0.8, "edgecolor": 'white'}
    # 外側のドーナツグラフ作成
    plt.rcParams['font.family'] = 'Arial Unicode MS'
    plt.pie(x=main_list, labels=main_labels, radius=1.3, startangle=90, counterclock=False, colors=main_colors,
            wedgeprops=wedgeprops)
    # 内側のドーナツグラフ作成
    plt.pie(x=sub_list, labels=sub_labels, startangle=90, counterclock=False, labeldistance=0.8, colors=sub_colors,
            wedgeprops=wedgeprops)
    # 凡例設定
    plt.legend(legend, fontsize=12, bbox_to_anchor=bbox_to_anchor)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')

    # csvにて保存（各件数について）
    file = file.replace('.png', '.csv')
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'a', encoding='utf-16') as f:
        writer_object = writer(f)
        writer_object.writerow(['No', 'Category', 'Count'])
        for row in legend:
            writer_object.writerow([row,
                                    category[legend.index(row)],
                                    (main_list + sub_list)[legend.index(row)]])
        f.close()


# 複数棒グラフ描写
def several_bar_plot_v(title='', x='', y='', hue='', data=None, palette=None, file=''):
    sns.barplot(x=x, y=y, hue=hue, data=data, palette=palette)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 棒グラフ描写
def bar_plot_v(title='', x='', y='', hue='', data=None, palette=None, file='', legend=None):
    sns.barplot(x=x, y=y, hue=hue, data=data, palette=palette)
    # 凡例非表示
    if not legend:
        plt.legend([], [], frameon=False)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 100%積み上げ棒グラフ描写
def bar_plot_100_v(title='', df=None, color=None, file=''):
    df.plot.bar(stacked=True, color=color)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 箱ひげ図描写
def box_plot_v(title='', x='', label_list=None, color_list=None, xlabel='', ylabel='',
               axhline=None, axhline_score=0, file=''):
    box = plt.boxplot(x=x,
                      labels=label_list,
                      patch_artist=True,  # 箱の塗りつぶし
                      showfliers=False,  # 外れ値は非表示
                      flierprops=dict(marker='x', color='black', markersize=2),  # 外れ値の表示設定
                      showmeans=True,  # 平均値を緑の三角で表示
                      medianprops={'color': 'black', 'linewidth': 3}  # 中央値の表示設定
                      )
    # 箱ひげ図を塗りつぶし
    for patch, color in zip(box['boxes'], color_list):
        patch.set_facecolor(color)
    # 水平線の描写
    if axhline:
        plt.axhline(y=axhline_score, color='black', linestyle='--')
    # X軸とY軸のラベル
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')


# 箱ひげ図2個描写
def double_box_plot_v(title='', data_list1=None, data_list2=None, data_label1='', data_label2='',
                      label_list=None, xlabel='', ylabel='', axhline=None, axhline_score=0, file=''):
    # グラフの作成
    fig, ax = plt.subplots()
    # positionsをラベルの数に応じて計算
    positions1 = numpy.arange(1, 2 * len(label_list), 2)
    positions2 = numpy.arange(1.6, 2 * len(label_list) + 0.6, 2)
    # 中央値の表示設定
    medianprops = {'color': 'black', 'linewidth': 3}
    # 1つ目の箱ひげ図
    ax.boxplot(data_list1,
               positions=positions1,
               widths=0.6,
               patch_artist=True,  # 箱の塗りつぶし
               boxprops=dict(facecolor='lightcoral'),
               showfliers=False,  # 外れ値は非表示
               showmeans=True,  # 平均値を緑の三角で表示
               medianprops=medianprops
               )

    # 2つ目の箱ひげ図
    ax.boxplot(data_list2,
               positions=positions2,
               widths=0.6,
               patch_artist=True,  # 箱の塗りつぶし
               boxprops=dict(facecolor='lightblue'),
               showfliers=False,  # 外れ値は非表示
               showmeans=True,  # 平均値を緑の三角で表示
               medianprops=medianprops
               )
    # ラベルの設定
    ax.set_xticks((positions1 + positions2) / 2)  # ラベルを中央に配置
    ax.set_xticklabels(label_list)
    # 凡例をまとめて出力する
    ax.legend(handles=[
        mpatches.Patch(color='lightcoral', label=data_label1),
        mpatches.Patch(color='lightblue', label=data_label2)],
        loc="lower center",
        bbox_to_anchor=(.5, 1.0), ncol=2)
    # 水平線の描写
    if axhline:
        plt.axhline(y=axhline_score, color='black', linestyle='--')
    # X軸とY軸のラベル
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.title(title)
    plt.savefig(file)
    plt.clf()
    plt.close('all')
