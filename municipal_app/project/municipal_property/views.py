# project/municipal_property/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from project.models import Proprietemunicipal, Municipality
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from .forms import ProprietyForm
from project import db
from pprint import pprint as pp
import datetime
import csv
import os

################
#### config ####
################

municipal_property_blueprint = Blueprint('municipal_property', __name__,)


################
#### routes ####
################

@municipal_property_blueprint.route('/add_municipal_property', methods=['GET', 'POST'])
@login_required
@check_confirmed
def add_municipal_property():
    form = ProprietyForm(request.form)
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name
    if form.validate_on_submit():
        mun_property = Proprietemunicipal(
            user_id=current_user.id,
            municipal_id=current_user.municipal_id,
            Titre_Foncier=form.Titre_Foncier.data,
            Type_du_Bien=form.Type_du_Bien.data,
            Adresse_Localisation=form.Adresse_Localisation.data,
            Mode_Octroi=form.Mode_Octroi.data,
            Surface=form.Surface.data,
            Longitude=form.Longitude.data,
            Laltitude=form.Laltitude.data,
            Type_Proprety=form.Type_Proprety.data,
            Type_Usage=form.Type_Usage.data
            )
        db.session.add(mun_property)
        db.session.commit()
        flash(u'تم حفظها في قاعدة البيانات', 'success')
        return redirect(url_for('municipal_property.consult_municipal_property'))
    return render_template('municipal_property/forms_municipal_property.html', form=form, update=False, mun_name=mun_name)


@municipal_property_blueprint.route('/consult_municipal_property', methods=['GET', 'POST'])
@login_required
@check_confirmed
def consult_municipal_property():
    data = [u.__dict__ for u in Proprietemunicipal.query.filter_by(municipal_id=current_user.municipal_id).all()]
    return render_template('municipal_property/municipal_property.html', data=data)


@municipal_property_blueprint.route('/update_municipal_property', methods=['GET', 'POST'])
@login_required
@check_confirmed
def update_municipal_property():
    property_id = request.values['type']
    save = True
    if len(request.values) > 3:
        if not check_float(request.values['Longitude']):
            flash(u'longitude verified format', 'warning')
            save = False
        if not check_float(request.values['Laltitude']):
            flash(u'laltitude verified format', 'warning')
            save = False
        if not check_float(request.values['Surface']):
            flash(u'surface verified format', 'warning')
            save = False
        if save:
            mun_property = Proprietemunicipal.query.get(int(property_id))
            mun_property.Longitude = float(request.values['Longitude'])
            mun_property.Laltitude = float(request.values['Laltitude'])
            mun_property.Adresse_Localisation = request.values['Adresse_Localisation']
            mun_property.Mode_Octroi = request.values['Mode_Octroi']
            mun_property.Surface = float(request.values['Surface'])
            mun_property.Titre_Foncier = request.values['Titre_Foncier']
            mun_property.Type_Usage = request.values['Type_Usage']
            mun_property.Type_du_Bien = request.values['Type_du_Bien']
            mun_property.Type_Proprety = request.values['Type_Proprety']
            db.session.commit()
            flash(u'تم تحيين الملك البلدي', 'success')
            return redirect(url_for('municipal_property.consult_municipal_property'))
    property_data = Proprietemunicipal.query.filter_by(id=property_id).first()
    return render_template('municipal_property/forms_municipal_property.html', update=True, property_data=property_data.__dict__)


@municipal_property_blueprint.route('/get_property_file', methods=['GET', 'POST'])
@login_required
@check_confirmed
def get_property_file():
    private_list, public_list = [], []
    if 'project' in url_for('main.home', _external=True) + 'static/files/':
        confirm_url = url_for('main.home', _external=True) + 'static/files/'
        confirm_url = confirm_url.replace('project', '')
    else:
        confirm_url = url_for('main.home', _external=True) + 'static/files/'
    data = [u.__dict__ for u in Proprietemunicipal.query.filter_by(municipal_id=current_user.municipal_id).all()]
    for d in data:
        if u'خاص' in d['Type_Proprety']:
            private_list.append(get_file_content(d))
        else:
            public_list.append(get_file_content(d))
    public_ref = 'properte_municipal_public_' + str(current_user.municipal_id)
    private_ref = 'properte_municipal_private_' + str(current_user.municipal_id)
    public_url = confirm_url + get_csv_file(public_list, public_ref, [])
    private_url = confirm_url + get_csv_file(private_list, private_ref, [])
    return render_template('municipal_property/municipal_property.html', data=data, file=True, public_url=public_url, private_url=private_url)


def check_float(value):
    try:
        float(value)
        return True
    except:
        return False


def get_csv_file(data, ref, field_list):
    _ = ['Titre_Foncier', 'Type_du_Bien', 'Mode_Octroi', 'Type_Usage', 'Surface', 'Adresse_Localisation', 'Longitude', 'Laltitude']
    fieldnames = _ + field_list
    filepath = get_file_path() + ref + '.csv'
    with open(filepath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    return ref + '.csv'


def get_file_content(d):
    data_dict = {'Longitude': d['Longitude'],
                 'Laltitude': d['Laltitude'],
                 'Adresse_Localisation': decode_unicode(d['Adresse_Localisation']),
                 'Mode_Octroi': decode_unicode(d['Mode_Octroi']),
                 'Surface': d['Surface'],
                 'Titre_Foncier': decode_unicode(d['Titre_Foncier']),
                 'Type_Usage': decode_unicode(d['Type_Usage']),
                 'Type_du_Bien': decode_unicode(d['Type_du_Bien']),
                }
    return data_dict


def decode_unicode(v):
    try:
        return v.encode('utf-8')
    except:
        return v


def get_file_path():
    if os.path.isdir('project/static/files/'):
        return 'project/static/files/'
    else:
        return "/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/project/static/files/"