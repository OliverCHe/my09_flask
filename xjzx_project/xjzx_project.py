from flask_script import Manager
from application import create_app
from config import DevelopmentConfig, Config
from flask_migrate import MigrateCommand, Migrate
from models import db
from flask_session import Session
from admin_command import CreateAdminCommand, RegisterUserCommand, HourLoginCommand

app = create_app(Config)

manager = Manager(app)

db.init_app(app)
Session(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command('createadmin', CreateAdminCommand)
manager.add_command('registeruser', RegisterUserCommand)
manager.add_command('HourLoginCommand', HourLoginCommand)

if __name__ == '__main__':
    manager.run()
