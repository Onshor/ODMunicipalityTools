# project/__init__.py


#################
#### imports ####
#################

import os
import logging
import sys
import datetime
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from werkzeug.debug import get_current_traceback
from config import ProductionConfig as APP_SETTINGS

################
#### config ####
################

app = Flask(__name__)

# app.config.from_object(os.environ['APP_SETTINGS'])
app.config.from_object(APP_SETTINGS)
# app.debug = True
####################
#### extensions ####
####################

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)


####################
#### blueprints ####
####################


from project.subvention.views import subvention_blueprint
from project.fourrier.views import fourrier_blueprint
from project.organigramme.views import organigram_blueprint
from project.passation_marche.views import passmarch_blueprint
from project.permis_construction.views import permisconst_blueprint
from project.budget.views import budget_blueprint
from project.main.views import main_blueprint
from project.user.views import user_blueprint
from project.admin.views import admin_blueprint
from project.municipal_property.views import municipal_property_blueprint
from project.ressource_manager.views import ressource_blueprint
app.register_blueprint(main_blueprint)
app.register_blueprint(subvention_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(budget_blueprint)
app.register_blueprint(fourrier_blueprint)
app.register_blueprint(organigram_blueprint)
app.register_blueprint(passmarch_blueprint)
app.register_blueprint(permisconst_blueprint)
app.register_blueprint(municipal_property_blueprint)
app.register_blueprint(ressource_blueprint)



####################
#### flask-login ####
####################

from project.models import User

login_manager.login_view = "user.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


def send_log_email(subject, template):
    msg = Message(
        subject,
        html=template,
        recipients=['med@onshor.org'],
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
########################
#### error handlers ####
########################


@app.errorhandler(403)
def forbidden_page(error):
    auth = True if current_user.__dict__ else False
    return render_template("errors/403.html", auth=auth), 403


@app.errorhandler(404)
def page_not_found(error):
    auth = True if current_user.__dict__ else False
    return render_template("errors/404.html", auth=auth), 404


@app.errorhandler(500)
def server_error_page(error):
    track = get_current_traceback(skip=1, show_hidden_frames=True, ignore_system_exceptions=False)
    html = render_template("errors/error_mail.html", stacktrace=str(track.plaintext))
    try:
        send_log_email(current_user.name + ' ' + current_user.last_name + ' ' + current_user.municipal_id + ' ' + str(datetime.datetime.now()), html)
        auth = True
    except:
        send_log_email('server_error', html)
        auth = False
    return render_template("errors/500.html", auth=auth), 500
