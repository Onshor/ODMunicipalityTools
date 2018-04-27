# manage.py

import datetime
import os
import unittest
import coverage

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from project import app, db
from project.models import User, Municipality
from list_municipality import municipalitys
from project.config import DevelopmentConfig as APP_SETTINGS


app.config.from_object(APP_SETTINGS)


migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(use_debugger=True, use_reloader=True))


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
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(User(
        email="med@onshor.org",
        password="admin",
        admin=True,
        confirmed=True,
        confirmed_on=datetime.datetime.now(),
        name='admin',
        last_name='admin',
        municipal_id='1',)
    )
    db.session.commit()


@manager.command
def create_test_user():
    """Creates the admin user."""
    db.session.add(User(
        email="med.dahas@esprit.com",
        password="medPWD17%%",
        admin=False,
        confirmed=True,
        confirmed_on=datetime.datetime.now(),
        name='med',
        last_name='dahas',
        municipal_id='72013',)
    )
    db.session.commit()


@manager.command
def create_municipality():
    """ Creates list of municipality """
    for m in municipalitys:
        db.session.add(Municipality(
            municipal_id=m['municipal_id'],
            municipal_name=m['municipal_name'],
            municipal_state=m['municipal_state']))
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
        #else:
        #    print(m)
        #    mun = Municipality.query.get(m['municipal_id'])
        #    mun.municipal_name = m['municipal_name']
        #    mun.municipal_name_ar = m['municipal_name_ar']
        #    mun.municipal_long = float(m['municipal_long'])
        #    mun.municipal_lat = float(m['municipal_lat'])
        #    db.session.commit()

if __name__ == '__main__':
    manager.run()
