# project/organigramme/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project.models import Organigramme
from project import db, app
import json
import os


################
#### config ####
################

organigram_blueprint = Blueprint('organigramme', __name__,)


################
#### routes ####
################

@organigram_blueprint.route('/organigramme', methods=['GET', 'POST'])
@login_required
@check_confirmed
def organigramme():
    if Organigramme.query.filter_by(municipal_id=current_user.municipal_id).first():
        json_organigramme = json.dumps(Organigramme.query.filter_by(municipal_id=current_user.municipal_id).first().organigramme_data)
        org_id = Organigramme.query.filter_by(municipal_id=current_user.municipal_id).first().id
        update = True
    else:
        json_organigramme = u'{"class": "go.TreeModel","nodeDataArray": [{"key": 1, "name": "(الاسم و اللقب)", "title": "", "email": "", "tel": "", "tel_fixe": ""}]}'
        update = False
    if 'javascript_data' in request.values:
        jdata = json.loads(request.values['javascript_data'])
        if update:
            org = Organigramme.query.get(org_id)
            org.organigramme_data = jdata
            db.session.commit()
        else:
            org = Organigramme(user_id=current_user.id,
                               municipal_id=current_user.municipal_id,
                               organigramme_data=jdata)
            db.session.add(org)
            db.session.commit()
        flash(u'تم تحيين التنظيم الهيكلي', 'success')
    confirm_url = url_for('main.home', _external=True) + 'static/files/'
    org_url = confirm_url + get_json_file(json_organigramme, 'organigramme_' + current_user.municipal_id)
    return render_template('organigramme/organigramme.html', json_organigramme=json_organigramme, org_file=org_url)


def get_json_file(data, ref):
    file_name = ref + '.json'
    filepath = get_file_path() + ref + '.json'
    with open(filepath, 'wb') as outfile:
        json.dump(data, outfile)
    return file_name


def get_file_path():
    if os.path.isdir('project/static/files/'):
        return 'project/static/files/'
    else:
        return "/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/project/static/files/"