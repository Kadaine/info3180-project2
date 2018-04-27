from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT

UPLOAD_FOLDER = './app/static/uploads'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'v\xf9\xf7\x11\x13\x18\xfaMYp\xed_\xe8\xc9w\x06\x8e\xf0f\xd2\xba\xfd\x8c\xda'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://project2:project2@localhost/project2"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
filefolder = app.config['UPLOAD_FOLDER']
Allowed_Uploads = ['jpg','png','jpeg']
app.debug= True
from app import views
