from cryptography.fernet import Fernet
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

fernet = None


def init_fernet(key):
    global fernet
    if key:
        if isinstance(key, str):
            key = key.encode()
        fernet = Fernet(key)
