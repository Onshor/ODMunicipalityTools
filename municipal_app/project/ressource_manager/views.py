# project/permis_construction/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from project.models import Municipality, Auto_update
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project.ressource_api import package_exists
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
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar
    if 'add_r_id' in request.values:
        update_ressource(request.values['add_r_id'], request.values['r_id'])
    if int(current_user.municipal_id) == 1:
        data = Auto_update.query.all()
        mun_name = None
    else:
        data = Auto_update.query.filter_by(municipal_id=current_user.municipal_id).all()
        mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar
    return render_template('ressource_manager/ressources.html', data=[u.__dict__ for u in data], mun_name=mun_name, location='/file_ressources')


@ressource_blueprint.route('/file_ressources/<location>/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def ressource_edit(id, location):
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar
    data = [Auto_update.query.filter_by(municipal_id=current_user.municipal_id, id=id).first()]
    if 'add_r_id' in request.values:
        link = url_for('main.home', _external=True) + 'static/files/' + Auto_update.query.filter_by(municipal_id=current_user.municipal_id, id=request.values['add_r_id']).first().file_name
        ressource_id = package_exists(link, current_user.api_key)
        if request.values['r_id'] in ressource_id:
            update_ressource(request.values['add_r_id'], request.values['r_id'])
            if 'consult_permisconst' in location:
                url = 'permis_construction.' + location
            elif 'consult_municipal_property' in location:
                url = 'municipal_property.' + location
            elif 'fourrier' in location:
                url = 'fourrier.' + location
            else:
                url = 'budget.' + location
            return redirect(url_for(url))
        else:
            flash(u'معرف ملف خاطئ أو غير موجودة بالمنصة البيانات المفتوحة', 'danger')
    return render_template('ressource_manager/ressources.html', data=[u.__dict__ for u in data], mun_name=mun_name, location='/' + location, upd=True)


def update_ressource(a_id, r_id):
    auto = Auto_update.query.get(int(a_id))
    auto.ressource_id = r_id
    db.session.commit()
    flash(u'تم تحيين / الاضافة', 'success')
    return 0