import sys
import os

# Adicione o diretório do seu projeto ao path do Python
path = '/home/YOUR_USERNAME/YOUR_PROJECT_NAME'
if path not in sys.path:
    sys.path.append(path)

from app import app as application

# Configuração para produção
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
application.config['SECRET_KEY'] = 'your-production-secret-key-here'
application.config['UPLOAD_FOLDER'] = os.path.join(path, 'static/uploads') 