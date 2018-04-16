# project/models.py


import datetime

from project import db, bcrypt


class Municipality(db.Model):
    __tablename__ = "municipality"
    municipal_id = db.Column(db.String, primary_key=True)
    municipal_name = db.Column(db.String, nullable=False)
    municipal_state = db.Column(db.String, nullable=False)

    def __init__(self, municipal_id, municipal_name, municipal_state):
        self.municipal_id = municipal_id
        self.municipal_name = municipal_name
        self.municipal_state = municipal_state

    def get_municipal_id(self):
        return self.municipal_id


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))

    def __init__(self, email, password, confirmed, name, municipal_id, last_name, paid=False, admin=False, confirmed_on=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.name = name
        self.last_name = last_name
        self.municipal_id = municipal_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}'.format(self.email)


class Budget_parametre(db.Model):
    __tablename__ = "budget_parametre"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String, nullable=False)
    article = db.Column(db.String, nullable=False)
    paragraphe = db.Column(db.String, nullable=False)
    sous_paragraphe = db.Column(db.String, nullable=False)
    titre = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=True)

    def __init__(self, user_id, article, type, paragraphe, sous_paragraphe, titre, label):
        self.user_id = user_id
        self.article = article
        self.type = type
        self.paragraphe = paragraphe
        self.sous_paragraphe = sous_paragraphe
        self.titre = titre
        self.label = label

    def get_id(self):
        return self.id


class Budget_annuelle(db.Model):
    __tablename__ = "budget_annuelle"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    parametre_id = db.Column(db.Integer, db.ForeignKey('budget_parametre.id'))
    montant = db.Column(db.Integer, nullable=True)
    numero_maj = db.Column(db.String, nullable=False)
    reference = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    insert_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, parametre_id, montant, municipal_id, numero_maj, reference, year, insert_date):
        self.parametre_id = parametre_id
        self.montant = montant
        self.municipal_id = municipal_id
        self.numero_maj = numero_maj
        self.reference = reference
        self.year = year
        self.insert_date = insert_date

    def get_id(self):
        return self.id


class Budget_mensuelle(db.Model):
    __tablename__ = "budget_mensuelle"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    parametre_id = db.Column(db.Integer, db.ForeignKey('budget_parametre.id'))
    montant = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __init__(self, parametre_id, montant, month, year, municipal_id):
        self.parametre_id = parametre_id
        self.montant = montant
        self.month = month
        self.year = year
        self.municipal_id = municipal_id

    def get_id(self):
        return self.id


class Permisconstruct(db.Model):
    __tablename__ = "permis_construction"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    num_demande = db.Column(db.String, nullable=True)
    date_depot = db.Column(db.DateTime, nullable=True)
    nom_titulaire = db.Column(db.String, nullable=True)
    num_cin = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String, nullable=True)
    type_construct = db.Column(db.String, nullable=True)
    desc_construct = db.Column(db.String, nullable=True)
    zone_municipal = db.Column(db.String, nullable=True)
    date_attribution = db.Column(db.DateTime, nullable=True)
    date_expiration = db.Column(db.DateTime, nullable=True)
    date_refuse = db.Column(db.DateTime, nullable=True)
    num_permis = db.Column(db.Integer, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    laltitude = db.Column(db.Float, nullable=True)
    permis_status = db.Column(db.String, nullable=True)
    mont_charge_fix = db.Column(db.Integer, nullable=True)
    mont_charge_ascend = db.Column(db.Integer, nullable=True)
    mont_cloture = db.Column(db.Integer, nullable=True)
    mont_decision = db.Column(db.Integer, nullable=True)
    mont_total = db.Column(db.Integer, nullable=True)


    def __init__(self, municipal_id, user_id, num_demande, date_depot, nom_titulaire, num_cin, type_construct, permis_status,
                 mont_cloture, mont_charge_ascend, mont_charge_fix, date_refuse, num_permis, zone_municipal, address, desc_construct,
                 date_attribution, date_expiration, longitude, laltitude, mont_decision, mont_total):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.num_demande = num_demande
        self.date_depot = date_depot
        self.nom_titulaire = nom_titulaire
        self.num_cin = num_cin
        self.zone_municipal = zone_municipal
        self.address = address
        self.desc_construct = desc_construct
        self.date_attribution = date_attribution
        self.date_expiration = date_expiration
        self.longitude = longitude
        self.laltitude = laltitude
        self.type_construct = type_construct
        self.permis_status = permis_status
        self.num_permis = num_permis
        self.date_refuse = date_refuse
        self.mont_charge_fix = mont_charge_fix
        self.mont_charge_ascend = mont_charge_ascend
        self.mont_cloture = mont_cloture
        self.mont_decision = mont_decision
        self.mont_total = mont_total

    def get_id(self):
        return self.id


class Proprietemunicipal(db.Model):
    __tablename__ = "propriete_municipal"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    Titre_Foncier = db.Column(db.String, nullable=True)
    Type_Usage = db.Column(db.String, nullable=True)
    Type_du_Bien = db.Column(db.String, nullable=True)
    Adresse_Localisation = db.Column(db.String, nullable=True)
    Mode_Octroi = db.Column(db.String, nullable=True)
    Surface = db.Column(db.Float, nullable=True)
    Longitude = db.Column(db.Float, nullable=True)
    Laltitude = db.Column(db.Float, nullable=True)
    Type_Proprety = db.Column(db.String, nullable=True)

    def __init__(self, municipal_id, user_id, Titre_Foncier, Type_du_Bien, Adresse_Localisation, Mode_Octroi,
                 Surface, Longitude, Laltitude, Type_Proprety, Type_Usage):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.Titre_Foncier = Titre_Foncier
        self.Type_du_Bien = Type_du_Bien
        self.Adresse_Localisation = Adresse_Localisation
        self.Mode_Octroi = Mode_Octroi
        self.Surface = Surface
        self.Longitude = Longitude
        self.Laltitude = Laltitude
        self.Type_Proprety = Type_Proprety
        self.Type_Usage = Type_Usage

    def get_id(self):
        return self.id