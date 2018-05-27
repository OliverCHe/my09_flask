class Config:
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'maysql://root:12345678@localhost:3306/my09_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
