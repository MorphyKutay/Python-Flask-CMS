from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for,session

app = Flask(__name__)
app.secret_key = 'your_unique_and_secret_key_here'
# MySQL bağlantı dizesini buraya ekleyin
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:1234@localhost/test' #kendi tablonuza göre editleyin

# SQLAlchemy uygulamasını başlatın
db = SQLAlchemy(app)


class Veri(db.Model):
    __tablename__ = 'veris' # kendi tablo adınızı ekleyin
    id = db.Column(db.Integer, primary_key=True) #kendi tablonuza göre editleyin
    uname = db.Column(db.String(64), nullable=False)#kendi tablonuza göre editleyin
    passw = db.Column(db.Integer, nullable=False) #kendi tablonuza göre editleyin

@app.route('/')
def login():
   return render_template('index.html')

@app.route('/check_login', methods=['POST'])
def check_login():
    username = request.form['username']
    password = request.form['password']

    # Veritabanından kullanıcıyı ara
    user = Veri.query.filter_by(uname=username, passw=password).first() # uname ve passw kısımlarına kendi tablonuzdaki username ve password adlarını yazınız

    if user:
        session['username'] = user.uname
        return redirect(url_for('dashboard'))

    else:
        return "Giriş başarısız! Lütfen kullanıcı adı ve şifrenizi kontrol edin."


@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=username)


if __name__ == '__main__':
    app.run(debug=True)