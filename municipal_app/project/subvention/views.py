# project/subvention/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from utils import *
from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project.models import Packages
from project.ckan_api import module_publisher
from project.util import check_role
from pprint import pprint as pp


################
#### config ####
################

subvention_blueprint = Blueprint('subvention', __name__,)
module_id = 5

################
#### routes ####
################


@subvention_blueprint.route('/subvention', methods=['GET', 'POST'])
@login_required
@check_confirmed
def subvention():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    link_data, _ = get_link_data()
    create = Packages.query.filter_by(modules_id=str(module_id), package_type='budget-association', municipal_id=current_user.municipal_id).first()
    if request.method == 'POST' and 'file_type' in request.values:
        if 'file' not in request.files:
            flash('No selected file', 'warning')
            return redirect(request.url)
        f = request.files['file']
        if f.filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            data, mun_id = parse_xml(f)
            if data and mun_id == current_user.municipal_id:
                save_db(data)
                link_data, _ = get_link_data()
                return render_template('subvention/subvention.html', link_data=link_data, create=create)
            else:
                flash(u'ملف خاطئ', 'danger')
                return url_for('subvention.subvention')
    if 'open_api' in request.values:
        link_data, year_str = get_link_data()
        module_publisher(module_id, 'budget-association', link_data, year_str, '', '')
        create = Packages.query.filter_by(modules_id=str(module_id), package_type='budget-association', municipal_id=current_user.municipal_id).first()
        return render_template('subvention/subvention.html', link_data=link_data, create=create)
    return render_template('subvention/subvention.html', link_data=link_data, create=create)
