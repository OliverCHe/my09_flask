from flask_script import Manager
from application import create_app
from config import DevelopmentConfig
from flask_migrate import MigrateCommand,Migrate
from models import db
from flask_session import Session

app = create_app(DevelopmentConfig)

manager = Manager(app)

db.init_app(app)
Session(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()