from flask import Flask, render_template, request, abort
from models import db, whooshee, Minwon


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WHOOSHEE_MIN_STRING_LEN'] = 2
db.init_app(app)
whooshee.init_app(app)


@app.route('/')
def index():
    #whooshee.reindex()
    return render_template('main.html')


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
        return render_template('search_result.html', opinions=final)
    else:
        abort(403)


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
