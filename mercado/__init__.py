from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mercado.db"
app.config["SECRET_KEY"] = '23f8fe9fabdb15a990b106f1'
db = SQLAlchemy()
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "page_login"
login_manager.login_message = "Por favor, realize o login"
login_manager.login_message_category = "info"

from mercado import routes