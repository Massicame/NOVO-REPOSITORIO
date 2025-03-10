from app import app, db
import os

def init_db():
    # Certifique-se de que o diretório static/uploads existe
    os.makedirs('static/uploads', exist_ok=True)
    
    # Criar o banco de dados
    with app.app_context():
        db.create_all()
        print("Banco de dados criado com sucesso!")

if __name__ == '__main__':
    init_db() 