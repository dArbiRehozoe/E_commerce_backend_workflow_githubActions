from flask import Blueprint
import os
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
#password_reset_bp = Blueprint('password_reset', __name__, url_prefix='/password_reset')
UPLOAD_FOLDER = os.path.abspath('uploads')
from app.routes import auth#, password_reset
