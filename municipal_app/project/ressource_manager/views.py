# project/permis_construction/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from project.models import Permisconstruct, Municipality, Auto_update
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project import db
from pprint import pprint as pp


################
#### config ####
################

ressource_blueprint = Blueprint('ressource', __name__,)


################
#### routes ####
################

@ressource_blueprint.route('/file_ressources', methods=['GET', 'POST'])
@login_required
@check_confirmed
def ressource():
    if int(current_user.municipal_id) == 1:
        data = Auto_update.query.all()
    else:
        data = Auto_update.query.filter_by(municipal_id=current_user.municipal_id).all()
    # pp([u.__dict__ for u in data])
    return render_template('ressource_manager/ressources.html', data=data)