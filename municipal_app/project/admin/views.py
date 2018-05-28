# project/admin/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed, check_admin
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project.models import User, Municipality
from pprint import pprint as pp


################
#### config ####
################


admin_blueprint = Blueprint('admin', __name__,)


@admin_blueprint.route('/admin')
@login_required
@check_confirmed
@check_admin
def admin():
    new_list = []
    list_user = [u.__dict__ for u in User.query.all()]
    for u in list_user:
        new_list.append({'confirmed': 'Oui' if u['confirmed'] else 'Non',
                         'confirmed_on': u['confirmed_on'].strftime("%d/%m/%Y") if u['confirmed'] and u['confirmed_on'] else None,
                         'name': u['name'],
                         'last_name': u['last_name'],
                         'municipality': Municipality.query.filter_by(municipal_id=u['municipal_id']).first().municipal_name if int(u['municipal_id']) != 1 else 'Super Admin',
                         'register_on': u['registered_on'].strftime("%d/%m/%Y"),
                         'admin': 'Oui' if u['admin'] else 'Non'})
    return render_template('admin/admin.html', list_user=new_list)