# project/models.py


import datetime
from sqlalchemy.dialects.postgresql import JSON
from project import db, bcrypt


class Municipality(db.Model):
    __tablename__ = "municipality"
    municipal_id = db.Column(db.String, primary_key=True)
    municipal_name = db.Column(db.String, nullable=False)
    municipal_state = db.Column(db.String, nullable=False)
    municipal_name_ar = db.Column(db.String, nullable=True)
    municipal_long = db.Column(db.Float, nullable=True)
    municipal_lat = db.Column(db.Float, nullable=True)
    approved = db.Column(db.Boolean, nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    ckan_id = db.Column(db.String)
    marssad_id = db.Column(db.String)

    def __init__(self, municipal_id, deleted, municipal_name, municipal_state, municipal_name_ar, municipal_long, municipal_lat, approved, ckan_id=None, marssad_id=None):
        self.municipal_id = municipal_id
        self.municipal_name = municipal_name
        self.municipal_state = municipal_state
        self.municipal_name_ar = municipal_name_ar
        self.municipal_long = municipal_long
        self.municipal_lat = municipal_lat
        self.approved = approved
        self.deleted = deleted
        self.ckan_id = ckan_id
        self.marssad_id = marssad_id

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
    last_login = db.Column(db.DateTime)
    deleted = db.Column(db.Boolean)
    activate = db.Column(db.Boolean)
    municipal_admin = db.Column(db.Boolean)
    phone_number = db.Column(db.Integer)
    work_position = db.Column(db.String)
    api_key = db.Column(db.String)
    ckan_id = db.Column(db.String)
    ckan_name = db.Column(db.String)

    def __init__(self, email, last_login, password, confirmed, name, municipal_id, last_name, deleted, activate, 
                 phone_number, work_position, ckan_id, ckan_name, api_key=None, paid=False, admin=False, confirmed_on=None, municipal_admin=False):
        self.deleted = deleted
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.name = name
        self.last_name = last_name
        self.municipal_id = municipal_id
        self.last_login = last_login
        self.activate = activate
        self.municipal_admin = municipal_admin
        self.phone_number = phone_number
        self.work_position = work_position
        self.api_key = api_key
        self.ckan_id = ckan_id
        self.ckan_name = ckan_name

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
    surface = db.Column(db.Float, nullable=True)
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
    refuse_note = db.Column(db.String, nullable=True)
    nom_architect = db.Column(db.String, nullable=True)
    reserve_note = db.Column(db.String, nullable=True)

    def __init__(self, municipal_id, user_id, num_demande, date_depot, nom_titulaire, num_cin, type_construct, permis_status,
                 mont_cloture, mont_charge_ascend, mont_charge_fix, date_refuse, num_permis, zone_municipal, address, desc_construct,
                 date_attribution, date_expiration, longitude, laltitude, mont_decision, mont_total, surface, refuse_note, nom_architect=None, reserve_note=None):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.num_demande = num_demande
        self.date_depot = date_depot
        self.surface = surface
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
        self.refuse_note = refuse_note
        self.nom_architect = nom_architect
        self.reserve_note = reserve_note

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


class Fourrier(db.Model):
    __tablename__ = "fourrier"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    Address_Fourrier = db.Column(db.String, nullable=True)
    Name_Fourrier = db.Column(db.String, nullable=True)
    Longitude = db.Column(db.Float, nullable=True)
    Laltitude = db.Column(db.Float, nullable=True)

    def __init__(self, municipal_id, user_id, Longitude, Laltitude, Address_Fourrier, Name_Fourrier):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.Address_Fourrier = Address_Fourrier
        self.Name_Fourrier = Name_Fourrier
        self.Longitude = Longitude
        self.Laltitude = Laltitude

    def get_id(self):
        return self.id


class Detention(db.Model):
    __tablename__ = "detention"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fourrier_id = db.Column(db.Integer, db.ForeignKey('fourrier.id'))
    Date_Detention = db.Column(db.DateTime, nullable=True)
    Cause_Detention = db.Column(db.String, nullable=True)
    Name_Owner = db.Column(db.String, nullable=True)
    Descr_Detention = db.Column(db.String, nullable=True)
    Authority_Detention = db.Column(db.String, nullable=True)
    Name_Fourrier = db.Column(db.String, nullable=True)
    Type_Detention = db.Column(db.String, nullable=True)
    Status_Detention = db.Column(db.String, nullable=True)
    Registration_Detention = db.Column(db.String, nullable=True)
    Date_Release = db.Column(db.String, nullable=True)
    Note = db.Column(db.String, nullable=True)
    Num_Bon = db.Column(db.String, nullable=True)
    montant_sortie = db.Column(db.Integer, nullable=True)

    def __init__(self, municipal_id, fourrier_id, user_id, Descr_Detention, Date_Detention, Cause_Detention,
                 Name_Owner, Authority_Detention, Name_Fourrier, Type_Detention, Registration_Detention,
                 Status_Detention, Date_Release,
                 Num_Bon, Note, montant_sortie=None):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.fourrier_id = fourrier_id
        self.Date_Detention = Date_Detention
        self.Cause_Detention = Cause_Detention
        self.Descr_Detention = Descr_Detention
        self.Type_Detention = Type_Detention
        self.Name_Owner = Name_Owner
        self.Authority_Detention = Authority_Detention
        self.Name_Fourrier = Name_Fourrier
        self.Registration_Detention = Registration_Detention
        self.Status_Detention = Status_Detention
        self.Date_Release = Date_Release
        self.Num_Bon = Num_Bon
        self.Note = Note
        self.montant_sortie = montant_sortie

    def get_id(self):
        return self.id


class Organigramme(db.Model):
    __tablename__ = "organigramme"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organigramme_data = db.Column(JSON, nullable=True)

    def __init__(self, municipal_id, organigramme_data, user_id):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.organigramme_data = organigramme_data

    def get_id(self):
        return self.id


class Auto_update(db.Model):
    __tablename__ = "auto_update"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    file_name = db.Column(db.String, nullable=True)
    ressource_id = db.Column(db.String, nullable=True)
    category = db.Column(db.String)

    def __init__(self, municipal_id, file_name, category, ressource_id=None):
        self.municipal_id = municipal_id
        self.file_name = file_name
        self.ressource_id = ressource_id
        self.category = category

    def get_id(self):
        return self.id


class File_log(db.Model):
    __tablename__ = "file_log"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('auto_update.id'))
    datetime_log = db.Column(db.DateTime)

    def __init__(self, municipal_id, user_id, file_id):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.file_id = file_id
        self.datetime_log = datetime.datetime.now()

    def get_id(self):
        return self.id


class Modules(db.Model):
    __tablename__ = "modules"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_ar = db.Column(db.String)

    def __init__(self, name, name_ar):
        self.name = name
        self.name_ar = name_ar

    def get_id(self):
        return self.id


class Users_Models(db.Model):
    __tablename__ = "users_modules"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    modules_id = db.Column(db.Integer, db.ForeignKey('modules.id'))

    def __init__(self, user_id, modules_id):
        self.user_id = user_id
        self.modules_id = modules_id

    def get_id(self):
        return self.id


class Data_Publisher(db.Model):
    __tablename__ = "data_publisher"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    modules_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    data_pub = db.Column(JSON)

    def __init__(self, municipal_id, user_id, modules_id, data_pub):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.modules_id = modules_id
        self.data_pub = data_pub

    def get_id(self):
        return self.id


class Resources(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    resource_id = db.Column(db.String)
    package_id = db.Column(db.String)
    link = db.Column(db.String)

    def __init__(self, municipal_id, resource_id, package_id, link):
        self.municipal_id = municipal_id
        self.resource_id = resource_id
        self.package_id = package_id
        self.link = link

    def get_id(self):
        return self.id


class Packages(db.Model):
    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    modules_id = db.Column(db.String)
    package_id = db.Column(db.String)
    package_type = db.Column(db.String)

    def __init__(self, municipal_id, modules_id, package_type, package_id):
        self.municipal_id = municipal_id
        self.modules_id = modules_id
        self.package_type = package_type
        self.package_id = package_id

    def get_id(self):
        return self.id


# class Datasets_log(db.Model):
#     __tablename__ = "datasets_log"
#     id = db.Column(db.Integer, primary_key=True)
#     municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
#     user_id = db.Column(db.String, db.ForeignKey('users.id'))
#     time_log = db.Column(db.String)
#     update = db.Column(db.Boolean)

#     def __init__(self, municipal_id, user_id, update):
#         self.municipal_id = municipal_id
#         self.user_id = user_id
#         self.time_log = datetime.datetime.now()
#         self.update = update

#     def get_id(self):
#         return self.id



class Budget_association(db.Model):
    __tablename__ = "budget_association"
    id = db.Column(db.Integer, primary_key=True)
    municipal_id = db.Column(db.String, db.ForeignKey('municipality.municipal_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    year = db.Column(db.String)
    ordre_numero = db.Column(db.String)
    benificiaire = db.Column(db.String)
    date_orde = db.Column(db.DateTime)
    date_paiement = db.Column(db.DateTime)
    montant_ordre = db.Column(db.Integer)
    montant_paiement = db.Column(db.Integer)

    def __init__(self, municipal_id, user_id, year, ordre_numero, benificiaire, date_orde, date_paiement, montant_ordre, montant_paiement):
        self.municipal_id = municipal_id
        self.user_id = user_id
        self.year = year
        self.ordre_numero = ordre_numero
        self.benificiaire = benificiaire
        self.date_orde = date_orde
        self.date_paiement = date_paiement
        self.montant_ordre = montant_ordre
        self.montant_paiement = montant_paiement

    def get_id(self):
        return self.id
