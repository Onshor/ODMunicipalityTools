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



@budget_blueprint.route('/budget')
@login_required
@check_confirmed
def budget():
    return render_template('budget/budget_annuel.html')