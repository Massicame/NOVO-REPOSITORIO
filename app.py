from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import logging
import re

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Por favor, preencha todos os campos')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                logger.info(f"Usuário {username} logado com sucesso")
                flash('Login realizado com sucesso!')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário ou senha incorretos')
                logger.warning(f"Tentativa de login falhou para usuário: {username}")
                
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            flash('Erro ao fazer login. Por favor, tente novamente.')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Validações
            if not username or not email or not password:
                flash('Por favor, preencha todos os campos')
                return redirect(url_for('register'))
            
            # Validar formato do email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Por favor, insira um email válido')
                return redirect(url_for('register'))
            
            # Validar tamanho da senha
            if len(password) < 6:
                flash('A senha deve ter pelo menos 6 caracteres')
                return redirect(url_for('register'))
            
            # Verificar se usuário já existe
            if User.query.filter_by(username=username).first():
                flash('Nome de usuário já existe')
                return redirect(url_for('register'))
                
            # Verificar se email já existe
            if User.query.filter_by(email=email).first():
                flash('Email já está em uso')
                return redirect(url_for('register'))
            
            # Criar novo usuário
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Novo usuário registrado: {username}")
            flash('Conta criada com sucesso! Por favor, faça login.')
            return redirect(url_for('login'))
            
        except Exception as e:
            logger.error(f"Erro no registro: {str(e)}")
            db.session.rollback()
            flash('Erro ao criar conta. Por favor, tente novamente.')
            
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
        try:
            if 'foto' not in request.files or 'documento' not in request.files:
                flash('Arquivos de foto e documento são obrigatórios')
                return redirect(request.url)
            
            foto = request.files['foto']
            documento = request.files['documento']
            
            if foto.filename == '' or documento.filename == '':
                flash('Selecione os arquivos necessários')
                return redirect(request.url)
            
            # Validar extensões dos arquivos
            allowed_image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            allowed_doc_extensions = {'pdf', 'doc', 'docx'}
            
            def allowed_file(filename, allowed_extensions):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
            
            if not allowed_file(foto.filename, allowed_image_extensions):
                flash('Formato de imagem não permitido. Use: png, jpg, jpeg, gif')
                return redirect(request.url)
                
            if not allowed_file(documento.filename, allowed_doc_extensions):
                flash('Formato de documento não permitido. Use: pdf, doc, docx')
                return redirect(request.url)
            
            # Gerar nomes de arquivo seguros
            foto_filename = secure_filename(foto.filename)
            documento_filename = secure_filename(documento.filename)
            
            # Garantir que os nomes são únicos
            foto_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{foto_filename}"
            documento_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{documento_filename}"
            
            # Salvar arquivos
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename)
            documento_path = os.path.join(app.config['UPLOAD_FOLDER'], documento_filename)
            
            foto.save(foto_path)
            documento.save(documento_path)
            
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
            flash('Registro criado com sucesso!')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.error(f"Erro ao criar registro: {str(e)}")
            db.session.rollback()
            flash('Erro ao criar registro. Por favor, tente novamente.')
            return redirect(request.url)
    
    return render_template('novo_registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
    app.run(debug=True) 