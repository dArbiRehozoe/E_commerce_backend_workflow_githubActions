from app import db
import datetime
class User(db.Model):
    iduser = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email  = db.Column(db.String(120), nullable=False)
    def __init__(self, username, password,email):
        self.username = username
        self.password = password
        self.email = email 
class Product(db.Model):
    idproduit  = db.Column(db.Integer, primary_key=True)
    qt = db.Column(db.Integer, nullable=False)
    design = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    categorie = db.Column(db.String(255), nullable=False)
    promo = db.Column(db.Integer, nullable=False)
    prix = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(255))
    corbeille=db.Column(db.Integer, nullable=False,default=1)
    def __init__(self,qt, design, description,categorie,promo,prix,image_path):
        self.design = design
        self.description = description
        self.qt=qt
        self.categorie=categorie
        self.promo=promo
        self.prix=prix
        self.image_path = image_path

class Commande(db.Model):
    idc=db.Column(db.Integer, primary_key=True)
    qt_produit= db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    num_facture= db.Column(db.String(500), nullable=False)
    adrss_liv=db.Column(db.String(500), nullable=False)
    idproduit = db.Column(db.String(500), nullable=False)
    iduser = db.Column(db.String(500), nullable=False)
    def __init__(self,qt_produit, num_facture,adrss_liv,idproduit,iduser):
        self.qt_produit = qt_produit
        #self.date=date
        self.num_facture=num_facture
        self.adrss_liv=adrss_liv
        self.idproduit = idproduit
        self.iduser = iduser

class Avis(db.Model):
    idavi = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Integer, nullable=False)
    iduser  = db.Column(db.String(120), nullable=False)
    idproduit  = db.Column(db.String(120), nullable=False)
    def __init__(self, note , iduser ,idproduit):
        self.note = note 
        self.iduser  = iduser 
        self.idproduit = idproduit
