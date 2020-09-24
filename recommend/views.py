from django.shortcuts import render
from django.http import HttpResponse

# 使用するライブラリのインポート
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


# Create your views here.
def recommend(request):
    # CSVファイルをデータフレーム形式として読み込み
    # 保存先が異なる場合はパスも指定してあげましょう
    ratings = pd.read_csv('csv/rating.csv')
    anime = pd.read_csv('csv/anime.csv')

    # # ratingのデータフレームの最初の5行を表示
    # print(ratings.head())
    # # ratingのデータフレームの最初の5行を表示
    # print(anime.head())

    # animeのデータフレームをmemberの値で並び替え
    anime_s = anime.sort_values('members', ascending=False)
    # print(anime_s.head())

    # animeの基本統計量の確認
    # print(round(anime.describe(), 2))

    # ratingsの基本統計量の確認
    # print(round(ratings.describe(), 2))

    # ratings['rating'].hist(bins=11, figsize=(10,10), color = 'red')

    # membersの値が10,000より大きいデータのみに変更
    anime = anime[anime['members'] > 10000]

    # 欠損データをdropna()でデータセットから取り除く
    anime = anime.dropna()

    # raitingの値が0以上のみ残す
    ratings = ratings[ratings.rating >= 0]

    # animeとratingsの2つのデータフレームをマージさせる
    mergeddf = ratings.merge(anime, left_on='anime_id', right_on='anime_id', suffixes=['_user', ''])
    # 合体したデータフレームの最初の5行を表示
    # print(mergeddf.head())

    # mergeddfの基本統計量の確認
    # print(round(mergeddf.describe(), 2))

    # 不必要な項目と重複項目を削除
    mergeddf = mergeddf[['user_id', 'name', 'rating_user']]
    mergeddf = mergeddf.drop_duplicates(['user_id', 'name'])
    # head()で最初の5行を表示
    # print(mergeddf.head())

    # データフレームのピボット
    anime_pivot = mergeddf.pivot(index='name', columns='user_id', values='rating_user').fillna(0)
    anime_pivot_sparse = csr_matrix(anime_pivot.values)

    # anime_pivotの最初の10行を表示
    # print(anime_pivot.head(10))

    # Scikit-learnのライブラリを利用します
    # n_neiborsやalgorithm、metricなど重要なアーギュメントを設定しています
    knn = NearestNeighbors(n_neighbors=9, algorithm='brute', metric='cosine')
    # 前処理したデータセットでモデルを訓練
    model_knn = knn.fit(anime_pivot_sparse)

    # データセットのタイトルをキーワードで検索
    def searchanime(string):
        print(anime_pivot[anime_pivot.index.str.contains(string)].index[0:])

    # print(searchanime('Hajime'))

    # 「君の名は」を見たことがあるあなたにオススメのアニメは・・・
    # Anime = 'Kimi no Na wa.'
    Anime = request.GET['anime']
    print(Anime)
    if Anime == "": Anime = 'Kimi no Na wa.'

    distance, indice = model_knn.kneighbors(anime_pivot.iloc[anime_pivot.index == Anime].values.reshape(1, -1),
                                            n_neighbors=11)
    for i in range(0, len(distance.flatten())):
        if i == 0:
            result = \
                'Recommendations if you like the anime {0}:<br/>'.format(
                    anime_pivot[anime_pivot.index == Anime].index[0])

            print(
               'Recommendations if you like the anime {0}:\n'.format(anime_pivot[anime_pivot.index == Anime].index[0]))


        else:
            result = result + \
                     '{0}: {1} with distance: {2} <br/>'.format(i, anime_pivot.index[indice.flatten()[i]],
                                                                distance.flatten()[i])

            print(
               '{0}: {1} with distance: {2}'.format(i, anime_pivot.index[indice.flatten()[i]], distance.flatten()[i]))

    return HttpResponse(result)
