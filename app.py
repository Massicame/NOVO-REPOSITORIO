from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    registrations = db.relationship('CattleBrand', backref='owner', lazy=True)

class CattleBrand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nome_marca = db.Column(db.String(100), nullable=False)
    bi = db.Column(db.String(20), nullable=False)
    nuit = db.Column(db.String(20), nullable=False)
    nr_caderneta = db.Column(db.String(50), nullable=False)
    foto_path = db.Column(db.String(200), nullable=False)
    documento_path = db.Column(db.String(200), nullable=False)
    contacto1 = db.Column(db.String(20), nullable=False)
    contacto2 = db.Column(db.String(20))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        registros = CattleBrand.query.all()
    else:
        registros = CattleBrand.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', registros=registros)

@app.route('/novo-registro', methods=['GET', 'POST'])
@login_required
def novo_registro():
    if request.method == 'POST':
        foto = request.files['foto']
        documento = request.files['documento']
        
        foto_filename = secure_filename(foto.filename)
        documento_filename = secure_filename(documento.filename)
        
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
        documento.save(os.path.join(app.config['UPLOAD_FOLDER'], documento_filename))
        
        registro = CattleBrand(
            nome=request.form['nome'],
            nome_marca=request.form['nome_marca'],
            bi=request.form['bi'],
            nuit=request.form['nuit'],
            nr_caderneta=request.form['nr_caderneta'],
            foto_path=foto_filename,
            documento_path=documento_filename,
            contacto1=request.form['contacto1'],
            contacto2=request.form.get('contacto2', ''),
            user_id=current_user.id
        )
        
        db.session.add(registro)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('novo_registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 