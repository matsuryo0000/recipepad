import os
from flask import (
     Flask, 
     request, 
     render_template,
     )

import datetime


from model import recommend #model.pyからrecommend関数をインポート

import sqlalchemy


engine = sqlalchemy.create_engine('sqlite:///test.db') #データベースエンジン作成
import sqlalchemy.ext.declarative
Base = sqlalchemy.ext.declarative.declarative_base() #ベースクラス作成


app = Flask(__name__)


class Post(Base): #テーブル定義
    __tablename__ = 'test'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True) #ナンバーリング
    item = sqlalchemy.Column(sqlalchemy.String(10), nullable=False) #食材
    fdate = sqlalchemy.Column(sqlalchemy.String(10), nullable=False) #賞味期限

Base.metadata.create_all(engine) #データベース登録

from sqlalchemy.orm import scoped_session, sessionmaker

session = scoped_session( #セッション作成（データの保存などの処理）
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = engine
        )
    )


@app.route('/', methods=['GET', 'POST']) #トップページのルーティング
def top():
    a = [[1,2,3],[4,5,6],[7,8,9]]

    return render_template('top.html', a=a)

@app.route('/scan', methods=['GET','POST']) #食材登録ページのルーティング
def scan():
    return render_template('scan.html')
    
    
    ###なし！
@app.route('/register', methods=['POST']) #登録処理のルーティング
def register():
    item = request.form["item"]
    fdate = request.form["fdate"]

    post = Post(item=item, fdate=fdate) #挿入
    session.add(post)
    session.commit()
    return render_template('scan.html')

@app.route('/search', methods=['GET','POST'])   #料理検索ページのルーティング
def search():
    posts = session.query(Post).all() #データ抽出（全て）

    day = datetime.date.today() #現在の日時
    day = str(day)

    for i in posts: #賞味期限切れ削除のルーティング
        if day > i.fdate:
            ii = session.query(Post).get(i.id) #テーブルデータからi番目のデータ取得
            print('iiの型は',type(ii))
            session.delete(ii) #i番目のデータ削除
            session.commit()

    
    return render_template('search.html',data=posts)
    
@app.route('/result', methods=['GET','POST'])   #出力ページのルーティング
def result():
    if request.method == "GET":
        return render_template('result.html')
    elif request.method == "POST":
       
        use_up = request.form.getlist("use_up") #使い切る（食材名、id）
        use = request.form.getlist("use") #まだ使う（食材名）
        use_items =[] #食材リスト作成
        use_ids =[] #IDリスト作成
        for i in range(len(use_up)):
            item,id=use_up[i].split(",") #[食材,ID]=use_up[i番目](","で分割)
            use_items.append(item)
            use_ids.append(id)

        use_list = use_items + use #食材全て=食材（使い切る）＋食材（まだ使う）

        for use_id in use_ids: #「食材IDとデータベースIDを比較→消去」の処理
            use_id = int(use_id)
            id_all = session.query(Post).all()

            for j in id_all:
                print('j型は',type(j))
                if j.id == use_id:
                    print('比較している')
                    use_delete = session.query(Post).get(j.id)
                    session.delete(use_delete)
                    session.commit() #ここまで！



        use_all = ",".join(use_list)
        print(use_all)
        recipe_all = recommend(use_all)
   

        return render_template('result.html', recipe_all=recipe_all)
    
    
if __name__ == '__main__':
    app.run(debug=True)