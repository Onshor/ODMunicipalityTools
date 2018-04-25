# project/passation_marche/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################


from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from pprint import pprint as pp

################
#### config ####
################

passmarch_blueprint = Blueprint('passation_marche', __name__,)


################
#### routes ####
################

@passmarch_blueprint.route('/passmarch')
@login_required
@check_confirmed
def passmarch():
    return render_template('passation_marche/passation_marche.html')
