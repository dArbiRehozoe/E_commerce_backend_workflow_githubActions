from decouple import config 
import os
# Configuration de la base de données MySQL
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI','mysql://root:root@db:3306/e_commerce')

# Clé secrète pour les sessions Flask
SECRET_KEY = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = config('MAIL_USERNAME')
MAIL_PASSWORD = config('MAIL_PASSWORD')
