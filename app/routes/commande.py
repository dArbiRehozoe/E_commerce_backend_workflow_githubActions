from flask import Blueprint, request,jsonify, Response
from app import db
from app.models import Commande
from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required
from app import app
from app.models import User
import datetime
from flask_cors import CORS

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from flask import Flask, redirect, url_for, request
import paypalrestsdk
from app.models import Product
from datetime import datetime, timedelta
import locale
from collections import OrderedDict
import json 
import os
commande_bp = Blueprint('commande', __name__)

CORS(commande_bp, resources={r"/effectuer-paiement": {"origins": "*"}})
# Configurer les informations d'API PayPal
URL_FRONT_END=os.environ.get('URL_FRONT_END','http://34.148.69.79/')
CLIENT_ID=os.environ.get('CLIENT_ID','AUN_wxnurjhXkMg3Fy5hT4kujnrgsKO_CFXEQ_76wv01SbGea1tfxk0MIhRBY6QG-AzbFgVeZQD3jVIZ')
CLIENT_SECRET=os.environ.get('CLIENT_SECRET','EC8EqZCYXifjMvFL4ooYyTFuP79yyD45p0Mqw1rel7ZKithrdRetytYpFEq88aYw1uAqMKAsab42m7yX')
paypalrestsdk.configure({
    "mode": "sandbox",  # Utilisez "live" pour les paiements en direct
    "client_id":CLIENT_ID,
    "client_secret":CLIENT_SECRET
})

@commande_bp.route("/effectuer-paiement", methods=['POST'])

def effectuer_paiement():
    data = request.get_json()
    print(data)
    panier = data["panier"]
    prix_total = data["prix_total"]
    iduser=data["iduser"]
    adresse=data["adresse"]
    # Créez un objet de paiement PayPal
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for("commande.confirmation_paiement", iduser=iduser, adresse=adresse, panier=panier,  _external=True),
            "cancel_url": url_for("commande.annuler_paiement", _external=True)
        },
        "transactions": [
            {
                "item_list": {
                    "items": panier 
                },
                "amount": {
                    "total": prix_total,
                    "currency": "USD"
                },
                "description": "Achat de(s) produit(s)"
            }
        ]
    })

    # Créez le paiement sur PayPal
    if payment.create():
        return jsonify(red=payment.links[1].href)
    else:
        return "Erreur lors de la création du paiement : {}".format(payment.error)

@commande_bp.route("/confirmation-paiement")
def confirmation_paiement():
    payer_id = request.args.get('PayerID')
    payment_id = request.args.get('paymentId')
    iduser = request.args.get('iduser')
    adresse = request.args.get('adresse')
    paniers = request.args.getlist('panier')
    print(paniers)

    try:
        panier_data = [json.loads(panier.replace("'", "\"")) for panier in paniers]
        liste_commandes = []  # Créez une liste pour stocker les commandes

        for item in panier_data:
            produit = Product.query.get(item["sku"])
            if produit:
                produit.qt -= int(item["quantity"])
            commande = Commande(
                qt_produit=int(item["quantity"]),
                num_facture=payment_id,  # Remplacez par un numéro de facture unique
                adrss_liv=adresse,
                iduser=iduser,
                idproduit=item["sku"],
                #date=datetime.datetime.now()
            )
            liste_commandes.append(commande)  # Ajoutez chaque commande à la liste

        # Ajoutez la liste entière de commandes à la base de données
        db.session.add_all(liste_commandes)
        db.session.commit()
        
        return redirect(url_for('commande.redirect_to_frontend'))
    except Exception as e:
        db.session.rollback()  # En cas d'erreur, annuler la transaction
        return f"Erreur lors du paiement : {str(e)}"
@commande_bp.route('/redirect-to-frontend')
def redirect_to_frontend():
    frontend_url = URL_FRONT_END  # Remplacez par l'URL de votre frontend React
    return redirect(frontend_url)

@commande_bp.route("/annuler-paiement")
def annuler_paiement():
    frontend_url = f"{URL_FRONT_END}/Panier"  # Remplacez par l'URL de votre frontend React
    return redirect(frontend_url)


@commande_bp.route('/commande', methods=['GET'])
def get_commande():
    commande = Commande.query.all()
    commande_list = []
    for commande in commande:
        commande_data = {
            'idc': commande.idc,
            'qt_produit': commande.qt_produit,
            'date': commande.date,
            'num_facture': commande.num_facture,
            'adrss_liv': commande.adrss_liv,
            'idproduit': commande.idproduit,
            'iduser' : commande.iduser
        }
        commande_list.append(commande_data)
    
    return jsonify(commande=commande_list)

@commande_bp.route('/add_commande', methods=['POST'])
def add_commande():
    data = request.get_json()
    qt_produit = data.get('qt_produit')
    date = datetime.datetime.now()
    num_facture = data.get('num_facture')
    adrss_liv = data.get('adrss_liv')
    idproduit = data.get('idproduit')
    iduser = data.get('iduser')
    new_commande = Commande( qt_produit=qt_produit,date=date,num_facture=num_facture,adrss_liv=adrss_liv,idproduit=idproduit,iduser=iduser)
    db.session.add(new_commande)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful'}), 201

from flask import jsonify
from app import db
from app.models import Commande, Product, User
@app.route('/donnees_commandes/<string:id_utilisateur>', methods=['GET'])
def obtenir_donnees_commandes(id_utilisateur):
    if (id_utilisateur=="1"):
        numeros_facture_distincts = db.session.query(Commande.num_facture).distinct().all()
    else:
    # Obtenez tous les numéros de facture distincts
        numeros_facture_distincts = db.session.query(Commande.num_facture).filter_by(iduser=id_utilisateur).distinct().all()

    # Créez une liste pour stocker les données de chaque commande
    resultats = []

    # Parcourez les numéros de facture distincts
    for num_facture in numeros_facture_distincts:
        # Obtenez toutes les commandes associées à ce numéro de facture
        commandes = Commande.query.filter_by(num_facture=num_facture[0]).all()

        # Créez une liste pour stocker les produits associés à cette facture
        produits_facture = []

        # Parcourez les commandes et obtenez les produits associés
        for commande in commandes:
            # Obtenez le produit associé à cette commande
            produit = Product.query.filter_by(idproduit=commande.idproduit).first()

            # Créez un dictionnaire pour stocker les données du produit
            donnees_produit = {
                "qt_produit": commande.qt_produit,
                "design": produit.design,
                "prix": produit.prix
            }

            # Ajoutez le produit à la liste des produits de la facture
            produits_facture.append(donnees_produit)

        # Obtenez l'utilisateur associé à cette facture (assumons qu'il est le même pour toutes les commandes de la facture)
        utilisateur_facture = User.query.filter_by(iduser=commandes[0].iduser).first()

        # Créez un dictionnaire pour stocker les données de la facture
        donnees_facture = {
            "num_facture": num_facture[0],
            "date": commandes[0].date.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "adrss_liv": commandes[0].adrss_liv,
            "produits": produits_facture,
            "total": sum(produit["qt_produit"] * produit["prix"] for produit in produits_facture),
            "email": utilisateur_facture.email,
            "pseudo": utilisateur_facture.username
        }

        # Ajoutez les données de la facture à la liste des résultats
        resultats.append(donnees_facture)

    # Convertissez les résultats en format JSON
    donnees_json = jsonify(resultats)

    # Vous pouvez maintenant renvoyer les données JSON comme réponse à votre requête GET
    return donnees_json


@app.route('/number_of_orders_by_category', methods=['GET'])
@jwt_required()
def number_of_orders_by_category():
    # Utilisez une requête SQL pour regrouper les commandes par catégorie de produit et calculer le prix total
    query = db.session.query(Product.categorie, db.func.sum(Commande.qt_produit * Product.prix).label('prixtotal')).\
        join(Commande, Commande.idproduit == Product.idproduit).\
        group_by(Product.categorie).all()

    # Créez une liste pour stocker les résultats sous forme d'objets JSON
    results = []
    for row in query:
        category, prixtotal = row
        results.append({"categorie": category, "prixtotal": prixtotal})

    # Convertissez la liste en JSON
    return jsonify(results)

@app.route('/total_money_spent_last_7_days_by_day', methods=['GET'])
@jwt_required()
def total_money_spent_last_7_days_by_day():
    # Configurez la locale en français
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    # Calculez la date il y a 7 jours à partir d'aujourd'hui
    seven_days_ago = datetime.now() - timedelta(days=7)

    # Initialisez un dictionnaire pour stocker les totaux par jour de la semaine
    totals_by_day = {'lundi': 0, 'mardi': 0, 'mercredi': 0, 'jeudi': 0, 'vendredi': 0, 'samedi': 0, 'dimanche': 0}

    # Récupérez les données de la base de données et agréguez-les par jour de la semaine
    commandes = db.session.query(Commande).filter(Commande.date >= seven_days_ago).all()
    for commande in commandes:
        # Utilisez la date de la commande pour obtenir le nom du jour de la semaine en français
        day_of_week = commande.date.strftime('%A').lower()  # Convertir en minuscules
        # Obtenez le produit associé à la commande
        produit = db.session.query(Product).get(commande.idproduit)
        if produit:
            # Assurez-vous que les valeurs sont converties en nombres avant l'addition
            montant_commande = int(commande.qt_produit) * int(produit.prix)
            totals_by_day[day_of_week] += montant_commande

    # Triez le dictionnaire en fonction de l'ordre des jours de la semaine en français
    sorted_totals = {day: totals_by_day[day] for day in ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']}

    # Convertissez le dictionnaire trié en JSON
    return jsonify(sorted_totals)


@app.route('/generate_pdf', methods=['POST'])
@jwt_required()
def generate_pdf():
    # Créer un fichier PDF
    data = request.get_json()
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Styles pour les paragraphes
    styles = getSampleStyleSheet()
    style = styles['Normal']
    if not data:
        return jsonify({"error": "Données manquantes dans la requête POST"}), 400
 
        # Ajouter le numéro de facture
    elements.append(Paragraph(f"Facture N° : {data['num_facture']}", style))
    elements.append(Spacer(1, 10)) 

        # Ajouter la date de paiement
    elements.append(Paragraph(f"Date de paiement: {data['date']}", style))

        # Ajouter l'adresse de livraison
    elements.append(Paragraph(f"Adresse de livraison: {data['adrss_liv']}", style))

        # Ajouter les produits
    elements.append(Paragraph("Produits: ", style))
    for produit in data['produits']:
            design = produit['design']
            prix = produit['prix']
            qt_produit = produit['qt_produit']
            # Espacement entre les produits
            elements.append(Paragraph(f"     Design: {design} - Prix: ${prix} - Quantité: {qt_produit}", style))

        # Ajouter le total net
    elements.append(Paragraph(f"Total net à payer: {data['total']} USD", style))

        # Espacement entre les factures
    elements.append(Spacer(1, 20))

    # Générer le PDF
    document.build(elements)

    # Retourner le PDF en tant que réponse HTTP
    buffer.seek(0)
    response = Response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename='+data['num_facture']
    return response

