from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for,session,flash,get_flashed_messages
from werkzeug.utils import secure_filename
import os

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

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


@app.route('/')
def index():
   posts = Posts.query.all() 
   return render_template('index.html',posts=posts)


@app.route('/login')
def login():
   return render_template('login.html')

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
        return render_template('login.html', message="Giriş başarısız! Lütfen kullanıcı adı ve şifrenizi kontrol edin.")


@app.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if title == "" or content =="":
            return redirect(url_for('dashboard'))
        new_post = Posts(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('dashboard'))

    posts = Posts.query.all()    
    return render_template('dashboard.html', username=username,active_page='dashboard',posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Posts.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/logout')
def logout():
    session.pop('username', None) #session'da saklanan username bilgisini kaldır 
    return redirect(url_for('login'))


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods = ['POST','GET'])
def upload():
    #user kontrol
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    #upload files
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Dosya seçilmedi.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Dosya adı boş olamaz.', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Dosya yüklenemedi İzin verilen dosya tipleri : txt, pdf, png, jpg, jpeg, gif', 'error')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Dosya başarıyla yüklendi: {}'.format(filename),'success')
        return redirect(url_for('upload'))
    
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER']) # yüklenen dosyaları listeler
    return render_template('upload.html', username=username, active_page='upload', messages=get_flashed_messages(),uploaded_files=uploaded_files)




@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    #dosya silme işlemi
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('Dosya başarıyla silindi: {}'.format(filename), 'success')
    else:
        flash('Dosya bulunamadı: {}'.format(filename), 'error')
    return redirect(url_for('upload'))


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    post = Posts.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/hakkimizda')
def hakkimizda():
     return redirect(url_for('index'))

@app.route('/iletisim')
def iletisim():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)