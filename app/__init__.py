from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
import os
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
UPLOAD_FOLDER = 'uploads'

app.config.from_object('app.config')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)
CORS(app)

from app.routes.product import product_bp
from app.routes.auth import auth_bp
from app.routes.commande import commande_bp
from app.routes.avis import avis_bp
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(commande_bp)
app.register_blueprint(avis_bp)