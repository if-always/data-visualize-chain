# coding:utf-8


from flask import *
import pymysql
import json
import pprint

app = Flask(__name__)
app.config.from_object(__name__)

def connectdb():
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='', db="douban", port=3306, charset='utf8')
    
    cursor = db.cursor()
    return (db,cursor)

# 关闭数据库
def closedb(db,cursor):
    db.close()
    cursor.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rate')
def rate():
    (db,cursor) = connectdb()
    cursor.execute("select rate, district, category, showtime, length from movie")
    desc = cursor.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
    movies = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

    #movies = cursor.fetchall()
    temp = []
    for item in movies:
        if not item['showtime'] == 0 and not item['length'] == 0:
            temp.append(item)
    movies = temp
    movies = json.dumps({"movies": movies})
    cursor.execute("select * from rate")
    desc = cursor.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
    rates = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

    #rates = cursor.fetchall()
    temp = {}
    for item in rates:
        temp[item['name']] = {}
        temp[item['name']]['categories'] = item['categories'].split(',')
        temp[item['name']]['rates'] = item['rates'].split(',')
        array = []
        for i in temp[item['name']]['rates']:
            array.append(float(i))
        temp[item['name']]['rates'] = array
    rates = temp
    pprint.pprint(rates)
    rates = json.dumps({"rates": rates})
    closedb(db,cursor)
    categories = ['剧情','喜剧','惊悚','爱情','动作','悬疑','犯罪','恐怖','科幻','冒险','奇幻','家庭','动画','战争','历史','古装','传记','音乐','同性','武侠','情色','灾难','运动','歌舞','西部','儿童','黑色电影','鬼怪','荒诞']
    districts = ['United States of America','China','Japan','South Korea','United Kingdom','France','Germany','Canada','Italy','Australia','Spain','Thailand','Russia','Belgium','Sweden','Ireland','Czech Republic','Denmark','India','Poland','Switzerland','New Zealand','Austria','Norway','Netherlands','Brazil','Hungary','Slovakia','Mexico','Iran','South Africa','Finland','Turkey','Romania','Luxembourg','Argentina','Iceland','Indonesia','Israel','United Arab Emirates','Malaysia','Georgia','Cuba','Kazakhstan','Estonia','Vietnam','Greece','Lithuania','Chile','Ukraine','Portugal','Bulgaria','Botswana','The Bahamas','Uzbekistan','Algeria','Puerto Rico','Philippines','Mauritania','Morocco','Latvia','Egypt','Myanmar','Tunisia','Peru','Colombia','Tajikistan']
    return render_template('rate.html',movies=movies,categories=categories,districts=districts,rates=rates)

@app.route('/search')
def search():
    (db,cursor) = connectdb()
    cursor.execute("select * from movie order by rate desc limit 10")
    desc = cursor.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
    movies = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

    #movies = cursor.fetchall()
    for item in movies:
        item['description'] = item['description'].split('/')
        item['composer'] = item['composer'].replace('/',' ')
        item['actor'] = item['actor'].replace('/',' ')
        item['category'] = item['category'].replace('/',' ')
        item['district'] = item['district'].split('/')
        temp = ''
        for d in item['district']:
            temp = temp + d.split('_')[1] + ' '
        item['district'] = temp[:-1]
        item['language'] = item['language'].replace('/',' ')
        item['othername'] = item['othername'].replace('/',' ')
    closedb(db,cursor)
    return render_template('search.html',movies=movies)

@app.route('/keyword',methods=['POST'])
def keyword():
    data = request.form
    print (data['keyword'])
    (db,cursor) = connectdb()
    cursor.execute("select * from movie where title like '%%%s%%' order by rate desc" % (data['keyword']))
    movies = cursor.fetchall()
    for item in movies:
        item['description'] = item['description'].split('/')
        item['composer'] = item['composer'].replace('/',' ')
        item['actor'] = item['actor'].replace('/',' ')
        item['category'] = item['category'].replace('/',' ')
        item['district'] = item['district'].split('/')
        temp = ''
        for d in item['district']:
            temp = temp + d.split('_')[1] + ' '
        item['district'] = temp[:-1]
        item['language'] = item['language'].replace('/',' ')
        item['othername'] = item['othername'].replace('/',' ')
    closedb(db,cursor)
    return json.dumps({"movies": movies})

if __name__ == '__main__':
    app.run(debug=True)