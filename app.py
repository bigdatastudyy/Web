from flask import Flask, render_template, request, abort, jsonify
from models import db, whooshee, Minwon
import pandas as pd
import sqlalchemy as sql
from minwon_search import set_query_topic,district_stats,monthly_topic_stats

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WHOOSHEE_MIN_STRING_LEN'] = 2
db.init_app(app)
whooshee.init_app(app)

# 희석쓰
sql_engine = sql.create_engine('sqlite:///final_data.db')
data = pd.read_sql_table('minwon_table',sql_engine)
data.date = pd.to_datetime(data.date)
a = data[data.date > '2018-08-01']
a.date = a.date.astype(str)

@app.route('/')
def index():
#    whooshee.reindex()
    return render_template('main.html')

@app.route('/test')
def test():
    c = district_stats(a, set_query_topic('송파구 가로등 보수작업'))
    return render_template('test.html',c=c)

@app.route('/search_result', methods=['POST'])
def search_page():
    if request.method == 'POST':
        search = request.form.get('search','None')
        if len(search) < 2:
            search = 'None'  # 2글자 이상
        if search=='None':
            abort(403)
        minwons = Minwon.query.whooshee_search(search, limit=900).order_by(Minwon.ans_date.desc()).all()
        n = 4
        final = [minwons[i * n:(i + 1) * n] for i in range((len(minwons) + n - 1) // n)]
        # 지역 rate
        c = district_stats(a,set_query_topic(search))
        # 월별
        d = monthly_topic_stats(a,'송파구',set_query_topic(search))
        return render_template('search_result.html', opinions=final,search=search,c=c,d=d)
    else:
        abort(403)


@app.route('/monthly_data', methods=["POST"])
def get_monthly_data():
    if request.method == "POST":
        name = request.form.get("name")
        search = request.form.get("search")

        return str(monthly_topic_stats(a, name, set_query_topic(search)))


@app.route('/detail_result/<index>')
def search_detail(index):
    minwons = Minwon.query.get(index)
    return render_template('detail_result.html', opinion=minwons)


@app.route('/search_area')
def search_area():
    return render_template('search_area.html')


@app.route('/issue')
def realtime_issue():
    return render_template('realtime_issue.html')


@app.route('/interest')
def interest():
    return render_template('interest.html')


@app.route('/local')
def local():
    return render_template('local.html')


if __name__ == '__main__':
    app.run()