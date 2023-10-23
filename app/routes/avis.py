from flask import Blueprint, request,jsonify
from app import db
from app.models import Avis
from flask_jwt_extended import jwt_required
avis_bp = Blueprint('avis', __name__)


@avis_bp.route('/liste_avis', methods=['GET'])
def liste_avis():
    avis = Avis.query.all()
    resultat = []

    for avis_item in avis:
        avis_details = {
            "idavi": avis_item.idavi,
            "note": avis_item.note,
            "iduser": avis_item.iduser,
            "idproduit": avis_item.idproduit
        }
        resultat.append(avis_details)

    # Convertissez les résultats en format JSON
    donnees_json = jsonify(resultat)

    # Renvoyez les données JSON comme réponse à votre requête GET
    return donnees_json

@avis_bp.route('/add_avis', methods=['POST'])
@jwt_required()
def add_avis():
    data = request.get_json()
    note = data.get('note')
    iduser = data.get('iduser')
    idproduit =data.get('idproduit')
    new_user = Avis(note=note, iduser=iduser,idproduit=idproduit)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201
@avis_bp.route('/update_avis/<int:idavi>', methods=['PUT'])
@jwt_required()
def update_avis(idavi):
    avi = Avis.query.get(idavi)
    if not avi:
        return jsonify({'message': 'Avis introuvable'}), 404

    data = request.get_json()  # Utilisez request.form pour obtenir les données du formulaire

    note = data.get('note')
    iduser = data.get('iduser')
    idproduit =data.get('idproduit')

    avi.note = note
    avi.iduser = iduser
    avi.idproduit = idproduit
    db.session.commit()
    return jsonify({'message': 'Produit mis à jour avec succès'}), 200

@avis_bp.route('/delete_avis/<int:idavi>', methods=['DELETE'])
@jwt_required()
def delete_idavi(idavi):
    avis = Avis.query.get(idavi)
    if not avis:
        return jsonify({'message': 'Avis introuvable'}), 404
    db.session.delete(avis)
    db.session.commit()
    return jsonify({'message': 'Avis supprimé avec succès'}), 200
@avis_bp.route('/verifier_avis/<int:iduser>/<int:idproduit>', methods=['GET'])
def verifier_avis(iduser, idproduit):
    # Recherchez un avis pour cette combinaison d'ID utilisateur et de produit
    avis_existe = Avis.query.filter_by(iduser=iduser, idproduit=idproduit).first()

    # Créez une réponse JSON indiquant si l'avis existe ou non
    reponse_json = jsonify({"avis_existe": avis_existe is not None})

    # Renvoyez la réponse JSON avec 'true' ou 'false'
    return reponse_json