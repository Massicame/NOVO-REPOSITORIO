# Sistema de Registro de Marcas de Gado

Sistema web para gestão de renovação de marcas de gado do Ministério da Agricultura, Ambiente e Pescas.

## Funcionalidades

- Autenticação de usuários (login/registro)
- Dashboard para visualização de registros
- Formulário de registro de marcas de gado
- Upload de fotos e documentos
- Visualização restrita por usuário
- Interface responsiva para dispositivos móveis

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

1. Certifique-se de que as pastas `static/uploads` e `static/images` existem
2. Coloque o logo do ministério em `static/images/logo.png`

## Executando o Sistema

1. Ative o ambiente virtual (se ainda não estiver ativo)
2. Execute o servidor:
```bash
python app.py
```
3. Acesse o sistema em `http://localhost:5000`

## Estrutura do Projeto

```
.
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências do projeto
├── static/            # Arquivos estáticos
│   ├── css/          # Arquivos CSS
│   ├── images/       # Imagens do sistema
│   └── uploads/      # Uploads dos usuários
└── templates/         # Templates HTML
    ├── base.html     # Template base
    ├── index.html    # Página inicial
    ├── login.html    # Página de login
    ├── register.html # Página de registro
    └── dashboard.html # Dashboard
```

## Segurança

- Senhas são armazenadas com hash
- Uploads são validados e seguros
- Acesso restrito por usuário
- Proteção contra CSRF
- Validação de formulários

## Suporte

Para suporte, entre em contato com a equipe de TI do Ministério da Agricultura, Ambiente e Pescas. 