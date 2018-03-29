# project/fourrier/views.py
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

fourrier_blueprint = Blueprint('fourrier', __name__,)


################
#### routes ####
################

@fourrier_blueprint.route('/fourrier')
@login_required
@check_confirmed
def fourrier():
    return render_template('fourrier/fourrier.html')