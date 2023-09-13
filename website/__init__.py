from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    APP_ROOT = path.dirname(path.abspath(__file__))

    # create folder to save new employee image
    UPLOAD_FOLD = 'my_db'
    UPLOAD_FOLDER = path.join(APP_ROOT, UPLOAD_FOLD)
    isExist = path.exists(UPLOAD_FOLDER)
    
    if not isExist:

        # Create a new directory because it does not exist
        os.makedirs(UPLOAD_FOLDER)
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        print("The new directory is created!")
    else:
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    #create folder to save recognized person image
    recognition_fold = "recognized"
    recognition_folder = path.join(APP_ROOT, recognition_fold)
    isExist_2 = path.exists(recognition_folder)

    if not isExist_2:

        # Create a new directory because it does not exist
        os.makedirs(recognition_folder)
        app.config['RECOGNITION_FOLDER'] = recognition_folder
        print("The new directory is created!")
    else:
        app.config['RECOGNITION_FOLDER'] = recognition_folder

    #create folder to save unknown person image
    unknown_fold = "unknown"
    unknown_folder = path.join(APP_ROOT, unknown_fold)
    isExist_3 = path.exists(unknown_folder)

    if not isExist_3:

        # Create a new directory because it does not exist
        os.makedirs(unknown_folder)
        app.config['UNKNOWN_FOLDER'] = unknown_folder
        print("The new directory is created!")
    else:
        app.config['UNKNOWN_FOLDER'] = unknown_folder

    #create folder to save Attendance sheets
    attendance_fold = "attendance"
    attendance_folder = path.join(APP_ROOT, attendance_fold)
    isExist_4 = path.exists(attendance_folder)

    if not isExist_4:

        # Create a new directory because it does not exist
        os.makedirs(attendance_folder)
        app.config['ATTENDANCE_FOLDER'] = attendance_folder
        print("The new directory is created!")
    else:
        app.config['ATTENDANCE_FOLDER'] = attendance_folder

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User #, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
     if not path.exists('website/' + DB_NAME):
         db.create_all(app=app)
         print('Created Database!')
