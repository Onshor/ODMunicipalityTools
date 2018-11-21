# manage.py
# -*- coding: utf-8 -*

import datetime
import os
import unittest
import coverage
import csv
from pandas import pandas as pd
from pprint import pprint as pp

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from project import app, db
from project.models import User, Municipality, Auto_update, Modules, Users_Models, Permisconstruct, Proprietemunicipal, Fourrier, Budget_parametre, File_log
from list_municipality import municipalitys
from project.config import DevelopmentConfig as APP_SETTINGS


app.config.from_object(APP_SETTINGS)


migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(use_debugger=True, use_reloader=True))
# manager.add_command("runserver", Server(use_reloader=True))


def read_csv(file):
    with open(file, 'rb') as f:
        return [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]


@manager.command
def test():
    """Runs the unit tests without coverage."""
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    cov = coverage.coverage(branch=True, include='project/*')
    cov.start()
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    print('Coverage Summary:')
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    cov.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    cov.erase()


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def create_new():
    """Creates the db tables."""
    db.create(Auto_update)


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def get_user_data():
    list_user = []
    email_list = ['med.dahas@gmail.com', 'kimoensi@gmail.com', 'kamel.mellah@gmail.com', 'mdalloua@fsvc.org', 'habib@onshor.org', 'bochra@metouia.com']
    list_user_db = [u.__dict__ for u in User.query.all()]
    for u in list_user_db:
        if not u['deleted'] and u['activate'] and int(u['municipal_id']) != 1 and u['email'] not in email_list:
            budget_data = True if Budget_parametre.query.filter_by(user_id=int(u['id'])).first() else False
            if not budget_data:
                list_file_budget = [_.id for _ in Auto_update.query.filter_by(municipal_id=u['municipal_id'], category='Budget').all()]
                for f in list_file_budget:
                    if File_log.query.filter_by(user_id=int(u['id']), file_id=int(f)).first():
                        budget_data = True
                        break
            list_user.append({'Municipalité': Municipality.query.filter_by(municipal_id=u['municipal_id']).first().municipal_name,
                              'Nom_Prenom': u['name'] + ' ' + u['last_name'],
                              'Fonction': u['work_position'],
                              'Tel': u['phone_number'],
                              'Date_Inscription': u['registered_on'].strftime("%m/%d/%Y"),
                              'Budget_Data': 'Oui' if budget_data else 'Non',
                              'Fourriere_Data': 'Oui' if Fourrier.query.filter_by(user_id=int(u['id'])).first() else 'Non',
                              'Permis_du_construction_Data': 'Oui' if Permisconstruct.query.filter_by(user_id=int(u['id'])).first() else 'Non',
                              'Property_municipal_Data': 'Oui' if Proprietemunicipal.query.filter_by(user_id=int(u['id'])).first() else 'Non'})
    pp(list_user)
    pp(len(list_user))
    df = pd.DataFrame(list_user)
    cols = ["Municipalité", "Nom_Prenom", "Fonction", "Tel", "Date_Inscription", "Budget_Data", "Fourriere_Data", "Permis_du_construction_Data", "Property_municipal_Data"]
    df.to_csv('list_users.csv', index=False, encoding='utf-8', columns=cols)
    return 0


@manager.command
def modules_db():
    """Create list module."""
    mod = [{'name': 'Budget', 'name_ar': u'الميزانية'},
           {'name': 'Permis_du_construction', 'name_ar': u'تراخيص البناء'},
           {'name': 'Fourriere', 'name_ar': u'الحجز البلدي'},
           {'name': 'Property_municipal', 'name_ar': u'الملك البلدي'}]
    for m in mod:
        db.session.add(Modules(
            name=m['name'],
            name_ar=m['name_ar']))
        db.session.commit()


@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(User(
        email="med@onshor.org",
        password="medPWD17%%",
        admin=True,
        confirmed=True,
        confirmed_on=datetime.datetime.now(),
        name='admin',
        last_name='admin',
        municipal_id='1',
        last_login=datetime.datetime.now(),
	    activate=True,
        deleted=False)
        # municipal_admin=False)
    )
    # db.session.add(User(
    #     email="boltanebochra@gmail.com",
    #     password='adminBochra17%%',
    #     admin=True,
    #     confirmed=True,
    #     confirmed_on=datetime.datetime.now(),
    #     name='Boltane',
    #     last_name='Bochra',
    #     municipal_id='1',)
    # )
    db.session.commit()


@manager.command
def create_test_user():
    """Creates the admin user."""
    db.session.add(User(
        email="med.dahas@test.com",
        password="medPWD17%%",
        admin=False,
        confirmed=True,
        confirmed_on=datetime.datetime.now(),
        name='med',
        last_name='dahas',
        municipal_id='34014',)
    )
    db.session.commit()


@manager.command
def create_municipality():
    """ Creates list of municipality """
    for m in municipalitys:
        db.session.add(Municipality(
            municipal_id='1',
            municipal_name='admin',
            municipal_state='admin',
            municipal_name_ar='admin',
            municipal_long=1,
            municipal_lat=1,
            approved=False,
            deleted=False))
        db.session.commit()


@manager.command
def user_module_set():
    list_user = [_.id for _ in User.query.all()]
    list_modules = [_.id for _ in Modules.query.all()]
    for u in list_user:
        for m in list_modules:
            if not Users_Models.query.filter_by(user_id=u, modules_id=m).first():
                db.session.add(Users_Models(
                    user_id=u,
                    modules_id=m))
                db.session.commit()
    return 0


@manager.command
def update_municipality_from_file():
    """ Creates list of municipality """
    mun_list = list(set([_.municipal_id for _ in Municipality.query.all()]))
    municipalits = read_csv('clean_mun_final.csv')
    list_approved = ['34012', '34011', '31011']
    for m in municipalits:
        if m['municipal_id'] not in mun_list:
            db.session.add(Municipality(
                municipal_id=m['municipal_id'],
                municipal_name=m['name'],
                municipal_state=m['state'],
                municipal_name_ar=m['name_ar'],
                municipal_long=m['lng'],
                municipal_lat=m['lat'],
                approved=True if m['municipal_id'] in list_approved else False,
                deleted=False))
            db.session.commit()


@manager.command
def update_municipality():
    """ Creates list of municipality """
    mun_list = list(set([_.municipal_id for _ in Municipality.query.all()]))
    for m in municipalitys:
        if m['municipal_id'] not in mun_list:
            db.session.add(Municipality(
                municipal_id=m['municipal_id'],
                municipal_name=m['municipal_name'],
                municipal_state=m['municipal_state'],
                municipal_name_ar=m['municipal_name_ar'],
                municipal_long=m['municipal_long'],
                municipal_lat=m['municipal_lat']))
            db.session.commit()
        else:
            mun = Municipality.query.get(m['municipal_id'])
            mun.municipal_name = m['municipal_name']
            mun.municipal_name_ar = m['municipal_name_ar']
            mun.municipal_long = float(m['municipal_long'])
            mun.municipal_lat = float(m['municipal_lat'])
            db.session.commit()

if __name__ == '__main__':
    manager.run()
