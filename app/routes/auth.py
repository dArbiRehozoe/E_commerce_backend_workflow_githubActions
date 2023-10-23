from flask import Blueprint, request, jsonify
from app.models import User
from app import db, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
import random
import string
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email =data.get('email')
    user_data = {
            'password': password,
            'username':username,
            'email':email
           
    }
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    existing_user = User.query.filter_by(username=username).first()
    existing_mail = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Ce pseudo est déjà utiliser, veillez chosir un autre'}),200
    if existing_mail:
        return jsonify({'message': 'Cette email est déjà associer a un compte'}),200


    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password,email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_data), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')  # Cela peut être un nom d'utilisateur ou un email
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'message': 'Missing username or password'}), 200

    # Essayez de trouver l'utilisateur par nom d'utilisateur ou email
    user = User.query.filter(db.or_(User.username == identifier, User.email == identifier)).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Pseudo ou Mots de passe incorrect'}), 200

    access_token = create_access_token(identity=identifier)
    user_data = {
            'access_token': access_token,
            'password': user.password,
            'username':user.username,
            'email':user.email,
            'iduser':user.iduser
    }
    return jsonify(user_data), 200


@auth_bp.route('/token', methods=['GET'])
@jwt_required()
def get_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token)


# Configuration SMTP (à adapter)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'williamjamesmoriart@gmail.com'
SMTP_PASSWORD = 'myslvzalgngeknxw'
EMAIL_SENDER = 'williamjamesmoriart@gmail.com'

# Dictionnaire pour stocker les codes de vérification associés aux adresses e-mail
verification_codes = {}

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    subject = "d'Ashop:Code de verification"
    message = f'Votre code de verification est : {code}'
    subject = subject.encode('utf-8')
    message = message.encode('utf-8')

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            server.sendmail(EMAIL_SENDER, email, f'Subject: {subject}\n\n{message}')
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")
        return False


@auth_bp.route('/request_verification_code', methods=['POST'])
def request_verification_code():
    data = request.get_json()
    if 'email' in data:
        email = data['email']
        code = generate_verification_code()
        verification_codes[email] = code
        if send_verification_email(email, code):
            return jsonify({'success': 'Code de vérification envoyé par e-mail'}), 200
        else:
            return jsonify({'message': 'Erreur lors de l\'envoi de l\'e-mail'}), 200
    else:
        return jsonify({'message': 'Adresse e-mail manquante'}), 200

@auth_bp.route('/verify_email', methods=['POST'])
def verify_email():
    data = request.get_json()
    if 'email' in data and 'code' in data and 'new_password' in data:
        email = data['email']
        code = data['code']
        new_password = data['new_password']

        if email in verification_codes and verification_codes[email] == code:
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash(new_password)  # Stockez le mot de passe haché
                db.session.commit()
                del verification_codes[email]  # Effacez le code de vérification
                return jsonify({'success': 'Mot de passe réinitialisé avec succès'}), 200
            else:
                return jsonify({'message': 'Adresse e-mail invalide'}), 200
        else:
            return jsonify({'message': 'Code de vérification incorrect'}), 200
    else:
        return jsonify({'message': 'Données manquantes'}), 200
    
@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    if 'iduser' in data:
        iduser = data['iduser']
        newpassword = data['newpassword']
        oldpassword = data['oldpassword']
            # Essayez de trouver l'utilisateur par nom d'utilisateur ou email
        user = User.query.filter_by(iduser=iduser).first()
        if not user or not check_password_hash(user.password, oldpassword):
            return jsonify({'message': 'Anciens Mots de passe invalide'}), 200
        if user:
            user.password = generate_password_hash(newpassword)  # Stockez le mot de passe haché
            db.session.commit()
             # Effacez le code de vérification
            return jsonify({'message': 'Mot de passe réinitialisé avec succès'}), 200
        else:
            return jsonify({'message': 'Adresse e-mail invalide'}), 400
    else:
        return jsonify({'message': 'Données manquantes'}), 400
@auth_bp.route('/change_username', methods=['POST'])
@jwt_required()
def change_username():
    data = request.get_json()
    if 'iduser' in data and 'username' in data:
        iduser = data['iduser']
        username = data['username']
        user = User.query.filter_by(iduser=iduser).first()
        if user:
            user.username = username  # Stockez le mot de passe haché
            db.session.commit()
             # Effacez le code de vérification
            return jsonify({'message': 'Pseudo mis a jour avec succès'}), 200
        else:
            return jsonify({'message': 'Adresse e-mail invalide'}), 400
    else:
        return jsonify({'message': 'Données manquantes'}), 400
    
@auth_bp.route('/change_email', methods=['POST'])
@jwt_required()
def change_email():
    data = request.get_json()
    if 'iduser' in data and 'email' in data:
        email = data['email']
        iduser = data['iduser']
        user = User.query.filter_by(iduser=iduser).first()
        if user:
            user.email = email  # Stockez le mot de passe haché
            db.session.commit()
             # Effacez le code de vérification
            return jsonify({'message': 'Email mis a jour avec succès'}), 200
        else:
            return jsonify({'message': 'Adresse e-mail invalide'}), 400
    else:
        return jsonify({'message': 'Données manquantes'}), 400
 
@auth_bp.route('/delete_user/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'user introuvable'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'compte supprimé avec succès'}), 200