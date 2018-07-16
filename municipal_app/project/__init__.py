# project/__init__.py


#################
#### imports ####
#################

import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
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


########################
#### error handlers ####
########################

@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500
