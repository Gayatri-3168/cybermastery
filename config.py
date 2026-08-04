# config.py
class Config:
    SECRET_KEY = "99215862073dee139271a22abc408835d70f69dbb46f0473baf3ba7c42bdd00e"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://cyber_user:Gayatri%403@localhost/cyber_game_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # EMAIL CONFIG
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "kgayatridevi2003@gmail.com"
    MAIL_PASSWORD = "yuxbgqjixtyowbtv"
    MAIL_DEFAULT_SENDER = "kgayatridevi2003@gmail.com"