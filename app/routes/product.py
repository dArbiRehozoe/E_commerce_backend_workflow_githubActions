from flask import  send_from_directory,Blueprint, request,jsonify
from app import db
from app.models import Product,Avis,User,Commande
from flask_jwt_extended import jwt_required
from app import app

import os
product_bp = Blueprint('product', __name__)
# @product_bp.route('/liste_produits', methods=['GET'])
# def liste_produits():
#     produits = Product.query.all()
#     resultat = []

#     for produit in produits:
#         # Obtenez les avis associés à ce produit
#         avis = Avis.query.filter_by(idproduit=produit.idproduit).all()

#         # Obtenez les adresses e-mail des utilisateurs qui ont donné leur avis
#         emails_utilisateurs = [User.query.get(avis_utilisateur.iduser).email for avis_utilisateur in avis]

#         # Calculer la note moyenne
#         notes = [avis_utilisateur.note for avis_utilisateur in avis]
#         note_moyenne = sum(notes) / len(notes) if notes else 0  # Évitez la division par zéro

#         # Créez un dictionnaire contenant les détails du produit, y compris la note moyenne
#         details_produit = {
#             "id":produit.idproduit,
#             "design": produit.design,
#             "description": produit.description,
#             "categorie": produit.categorie,
#             "promo": produit.promo,
#             "prix": produit.prix,
#             "image_path": produit.image_path,
#             "avis": [{"email_utilisateur": email} for avis_utilisateur, email in zip(avis, emails_utilisateurs)],
#             "note_moyenne": note_moyenne  # Ajoutez la note moyenne au dictionnaire
#         }

#         # Ajoutez le dictionnaire à la liste des résultats
#         resultat.append(details_produit)

#     # Convertissez les résultats en format JSON
#     donnees_json = jsonify(resultat)

#     # Renvoyez les données JSON comme réponse à votre requête GET
#     return donnees_json
@product_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {
            'idproduit': product.idproduit,
            'qt': product.qt,
            'description': product.description,
            'categorie': product.categorie,
            'design': product.design,
            'promo': product.promo,
            'prix': product.prix,
        }
        
        if product.image_path:
            # Si un chemin d'accès à l'image est défini, incluez-le dans les données du produit
            product_data['image_path'] = product.image_path
        
        product_list.append(product_data)
    
    return jsonify(products=product_list)

@product_bp.route('/products/<string:cat_produit>', methods=['GET'])
def get_productsCategorie(cat_produit):
    products = Product.query.filter_by(categorie=cat_produit).all()
    product_list = []
    for product in products:
        product_data = {
            'idproduit': product.idproduit,
            'qt': product.qt,
            'description': product.description,
            'categorie': product.categorie,
            'design': product.design,
            'promo': product.promo,
            'prix': product.prix,
        }
        
        if product.image_path:
            # Si un chemin d'accès à l'image est défini, incluez-le dans les données du produit
            product_data['image_path'] = product.image_path
        
        product_list.append(product_data)
    
    return jsonify(products=product_list)
# Déplacez ces fonctions utilitaires vers un fichier utils.py si vous le souhaitez
def create_product(qt, design, description, categorie, promo, prix, image_path=None):
    new_product = Product(qt, design, description, categorie, promo, prix, image_path=image_path)
    db.session.add(new_product)
    db.session.commit()
    return new_product

# Route pour créer un produit avec téléchargement d'image
@product_bp.route('/add_product', methods=['POST'])
@jwt_required()
def add_product():
    data = request.form  # Utilisez request.form pour obtenir les données du formulaire
    print(data)
    design = data['design']
    qt = int(data['qt'])
    description = data['description']
    categorie = data['categorie']
    promo = int(data['promo'])
    prix = int(data['prix'])

    # Gérez le téléchargement de l'image
    if 'file' not in request.files:
        return jsonify({'message': 'Aucun fichier n\'a été sélectionné'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'Aucun fichier n\'a été sélectionné'}), 400

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        image_path = filename  # Utilisez le chemin d'accès à l'image pour la base de données

    # Créez le produit avec les détails et le chemin d'accès de l'image
    new_product = create_product(qt, design, description, categorie, promo, prix, image_path)

    return jsonify({'message': 'Produit ajouté avec succès', 'product_id': new_product.idproduit}), 200

@product_bp.route('/update_product/<int:idproduit>', methods=['PUT'])
@jwt_required()
def update_product(idproduit):
    product = Product.query.get(idproduit)
    if not product:
        return jsonify({'message': 'Produit introuvable'}), 404

    data = request.form  # Utilisez request.form pour obtenir les données du formulaire

    qt = int(data['qt'])
    design = data['design']
    description = data['description']
    categorie = data['categorie']
    promo = int(data['promo'])
    prix = int(data['prix'])

    # Gérez la mise à jour du chemin d'accès de l'image si une nouvelle image est téléchargée
    if 'file' in request.files:
        file = request.files['file']

        if file.filename != '':
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            product.image_path = filename  # Mettez à jour le chemin d'accès de l'image

    # Mettez à jour les autres champs du produit
    product.qt = qt
    product.design = design
    product.description = description
    product.categorie = categorie
    product.promo = promo
    product.prix = prix

    db.session.commit()
    return jsonify({'message': 'Produit mis à jour avec succès'}), 200

@product_bp.route('/delete_product/<int:idproduit>/<int:corbeille>', methods=['DELETE'])
@jwt_required()
def delete_product(idproduit,corbeille):
    product = Product.query.get(idproduit)
    if not product:
        return jsonify({'message': 'Produit introuvable'}), 404
    if corbeille==0:
        product.corbeille=1
    else:
        product.corbeille=0
    db.session.commit()
    return jsonify({'message': 'Produit supprimé avec succès'}), 200

@product_bp.route('/liste_produits/<string:nom_utilisateur>', methods=['GET'])
def liste_produits(nom_utilisateur):
    produits = Product.query.all()
    resultat = []

    for produit in produits:
        # Obtenez les avis associés à ce produit
        avis = Avis.query.filter_by(idproduit=produit.idproduit).all()

      

        # Recherchez si l'utilisateur a laissé un avis pour ce produit
        avis_utilisateur = Avis.query.filter_by(idproduit=produit.idproduit, iduser=nom_utilisateur).first()
        commande = Commande.query.filter_by(idproduit=produit.idproduit, iduser=nom_utilisateur).first()
        # Si l'utilisateur a laissé un avis, obtenez son ID d'avis et sa note
        idavie = avis_utilisateur.idavi if avis_utilisateur else None
        note = avis_utilisateur.note if avis_utilisateur else None
        commande = True if commande else False
        # Calculer la note moyenne
        notes = [avis_utilisateur.note for avis_utilisateur in avis]
        note_moyenne = sum(notes) / len(notes) if notes else 0  # Évitez la division par zéro

        # Créez un dictionnaire contenant les détails du produit, y compris la note moyenne, l'ID d'avis et la note de l'utilisateur
        details_produit = {
            "id":produit.idproduit,
            "design": produit.design,
            "description": produit.description,
            "categorie": produit.categorie,
            "promo": produit.promo,
            "prix": produit.prix,
            "image_path": produit.image_path,
            "note_moyenne": note_moyenne,
            "idavie": idavie,
            "note_utilisateur": note,
            "commande":commande,
            "qt":produit.qt,
            "corbeille":produit.corbeille
        }
    
        # Ajoutez le dictionnaire à la liste des résultats
        resultat.append(details_produit)

    # Convertissez les résultats en format JSON
    donnees_json = jsonify(resultat)

    # Renvoyez les données JSON comme réponse
    return donnees_json

@product_bp.route('/produitA', methods=['GET'])
def produitA():
    produits = Product.query.all()
    resultat = []

    for produit in produits:
        details_produit = {
            "id":produit.idproduit,
            "design": produit.design,
            "description": produit.description,
            "categorie": produit.categorie,
            "promo": produit.promo,
            "prix": produit.prix,
            "image_path": produit.image_path,        
        }
    
        # Ajoutez le dictionnaire à la liste des résultats
        resultat.append(details_produit)

    # Convertissez les résultats en format JSON
    donnees_json = jsonify(resultat)

    # Renvoyez les données JSON comme réponse
    return donnees_json


@product_bp.route('/liste_produits/<string:nom_utilisateur>/<string:cat_produit>', methods=['GET'])
@jwt_required()
def liste_produitsCategorie(nom_utilisateur,cat_produit):
    produits =Product.query.filter_by(categorie=cat_produit).all()
    resultat = []

    for produit in produits:
        # Obtenez les avis associés à ce produit
        avis = Avis.query.filter_by(idproduit=produit.idproduit).all()



        # Recherchez si l'utilisateur a laissé un avis pour ce produit
        avis_utilisateur = Avis.query.filter_by(idproduit=produit.idproduit, iduser=nom_utilisateur).first()
        commande = Commande.query.filter_by(idproduit=produit.idproduit, iduser=nom_utilisateur).first()
        # Si l'utilisateur a laissé un avis, obtenez son ID d'avis et sa note
        idavie = avis_utilisateur.idavi if avis_utilisateur else None
        note = avis_utilisateur.note if avis_utilisateur else None
        commande = True if commande else False
        # Calculer la note moyenne
        notes = [avis_utilisateur.note for avis_utilisateur in avis]
        note_moyenne = sum(notes) / len(notes) if notes else 0  # Évitez la division par zéro

        # Créez un dictionnaire contenant les détails du produit, y compris la note moyenne, l'ID d'avis et la note de l'utilisateur
        details_produit = {
            "id":produit.idproduit,
            "design": produit.design,
            "description": produit.description,
            "categorie": produit.categorie,
            "promo": produit.promo,
            "prix": produit.prix,
            "image_path": produit.image_path,
            "note_moyenne": note_moyenne,
            "idavie": idavie,
            "note_utilisateur": note,
            "commande":commande,
            "qt":produit.qt,
            "corbeille":produit.corbeille
        }
    
        # Ajoutez le dictionnaire à la liste des résultats
        resultat.append(details_produit)

    # Convertissez les résultats en format JSON
    donnees_json = jsonify(resultat)

    # Renvoyez les données JSON comme réponse
    return donnees_json
@product_bp.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory( os.path.abspath('uploads'), filename)



