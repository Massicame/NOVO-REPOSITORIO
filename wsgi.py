import sys
import os

# Adicione o diretório do seu projeto ao path do Python
path = '/home/000144/NOVO-REPOSITORIO'
if path not in sys.path:
    sys.path.append(path)

from app import app as application, db

# Configuração para produção
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
application.config['SECRET_KEY'] = 'your-production-secret-key-here'
application.config['UPLOAD_FOLDER'] = os.path.join(path, 'static/uploads')

# Garantir que o diretório de uploads existe
os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)

# Criar o banco de dados se não existir
with application.app_context():
    try:
        db.create_all()
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {str(e)}")

# Configurar logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(path, 'error.log')),
        logging.StreamHandler()
    ]
) 