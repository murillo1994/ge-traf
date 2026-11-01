import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///getraf.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    FERNET_KEY = os.environ.get("FERNET_KEY")
    META_APP_ID = os.environ.get("META_APP_ID")
    META_APP_SECRET = os.environ.get("META_APP_SECRET")
    META_REDIRECT_URI = os.environ.get("META_REDIRECT_URI")
    METABASE_SECRET_KEY = os.environ.get("METABASE_SECRET_KEY")
    METABASE_SITE_URL = os.environ.get("METABASE_SITE_URL", "http://localhost:3000")
    METABASE_DASHBOARD_ID = int(os.environ.get("METABASE_DASHBOARD_ID", "1"))


class DevelopmentConfig(Config):
    DEBUG = True
    FERNET_KEY = os.environ.get(
        "FERNET_KEY", "RYJ5GII1AdUF4SqN-f4_63BPtIXpIgegDrSHfEiLiZg="
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    FERNET_KEY = "RYJ5GII1AdUF4SqN-f4_63BPtIXpIgegDrSHfEiLiZg="
    SERVER_NAME = "localhost"


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
