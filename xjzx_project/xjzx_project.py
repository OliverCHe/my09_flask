from flask_script import Manager
from application import create_app
from config import DevelopmentConfig
from flask_migrate import MigrateCommand,Migrate
from models_1 import db

app = create_app(DevelopmentConfig)

manager = Manager(app)

db.init_app(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()