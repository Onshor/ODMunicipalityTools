# project/permis_construction/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask.ext.login import login_required, current_user
from .forms import PermisconstructForm
from pprint import pprint as pp

################
#### config ####
################

permisconst_blueprint = Blueprint('permis_construction', __name__,)


################
#### routes ####
################

@permisconst_blueprint.route('/permisconst', methods=['GET', 'POST'])
@login_required
@check_confirmed
def permisconst():
    form = PermisconstructForm(request.form)
    if form.validate_on_submit():
        pp(True)
        return redirect(url_for('permis_construction.permisconst'))
    return render_template('permis_construction/permis_construction.html', form=form)
