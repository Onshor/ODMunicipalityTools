# project/organigramme/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask.ext.login import login_required, current_user
from pprint import pprint as pp

################
#### config ####
################

organigram_blueprint = Blueprint('organigramme', __name__,)


################
#### routes ####
################

@organigram_blueprint.route('/organigramme')
@login_required
@check_confirmed
def organigramme():
    return render_template('organigramme/organigramme.html')