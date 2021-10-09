from os import path


class Config:
    APP_DIR = path.dirname(path.abspath(__file__))
    BASE_DIR = path.dirname(APP_DIR)
    DEBUG = True
    SECRET_KEY = "1a45ac651d8a1b42bd8c43dbe4e0a2f696374ce5ab50ec7d"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/db.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
