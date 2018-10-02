# project/budget/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from utils import *
from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from parser import parse_budget, parse_recette_file, parse_depence_file
from project.models import Budget_annuelle, Municipality, Auto_update
from list_month import decode_month_ar, decode_month_fr
from project.ressource_api import update_ressource_api, update_ressource_api_request, package_exists
from pprint import pprint as pp





################
#### config ####
################

budget_blueprint = Blueprint('budget', __name__,)


################
#### routes ####
################


@budget_blueprint.route('/budget/<types>')
@login_required
@check_confirmed
def budget(types):
    if types in 'annuel':
        if Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id).first():
            data = get_budget_files()
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No selected file')
                    return redirect(request.url)
                f = request.files['file']
                if f.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if f and allowed_file(f.filename):
                    pp()
            return render_template('budget/budget_annuel.html', data=data, parsed_annuel=True)
        return render_template('budget/budget_annuel.html')
    elif types in 'depence_mensuelle':
        return render_template('budget/budget_depence_mensuelle.html')
    else:
        return render_template('budget/budget_recette_mensuelle.html')