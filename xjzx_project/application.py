from flask import Flask
from views_news import news_blueprint
from views_user import user_blueprint
from views_admin import admin_blueprint

def create_app(DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    app.register_blueprint(news_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)

    return app