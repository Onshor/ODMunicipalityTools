# project/permis_construction/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from project.models import Permisconstruct, Municipality
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from .forms import PermisencourForm, PermisrefuseForm, PermisupdateForm
from project import db
import os
import datetime
import csv


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
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name
    mun_long = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_long
    mun_lat = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_lat
    form = PermisencourForm(request.form)
    if form.validate_on_submit():
        permis = Permisconstruct(municipal_id=current_user.municipal_id,
                                 user_id=current_user.id,
                                 num_demande=form.num_demande.data,
                                 date_depot=form.date_depot.data,
                                 nom_titulaire=form.nom_titulaire.data,
                                 num_cin=form.num_cin.data,
                                 address=form.address.data,
                                 type_construct=form.type_construct.data,
                                 desc_construct=form.desc_construct.data,
                                 zone_municipal=form.zone_municipale.data,
                                 longitude=form.longitude.data,
                                 laltitude=form.latitude.data,
                                 permis_status='en_cours',
                                 num_permis=None,
                                 date_attribution=None,
                                 date_expiration=None,
                                 date_refuse=None,
                                 mont_charge_fix=0,
                                 mont_charge_ascend=0,
                                 mont_cloture=0,
                                 mont_decision=0,
                                 mont_total=0,
                                 surface=form.surface.data,
                                 refuse_note=None
                                 )
        db.session.add(permis)
        db.session.commit()
        flash(u'تم حفظها في قاعدة البيانات', 'success')
        return redirect(url_for('permis_construction.consult_permisconst'))
    return render_template('permis_construction/form_permis_construction.html', form=form, update=False, permis_id=None, mun_name=mun_name, mun_cord=[mun_lat, mun_long])


@permisconst_blueprint.route('/consult_permisconst', methods=['GET', 'POST'])
@login_required
@check_confirmed
def consult_permisconst():
    if 'delete_row' in request.values:
        p_id = Permisconstruct.query.get(int(request.values['type']))
        db.session.delete(p_id)
        db.session.commit()
        flash(u'تم فسخ الرخصة', 'success')
        return redirect(url_for('permis_construction.consult_permisconst'))
    data = [u.__dict__ for u in Permisconstruct.query.filter_by(municipal_id=current_user.municipal_id).all()]
    return render_template('permis_construction/permis_construction.html', data=data)


@permisconst_blueprint.route('/update_permisconst', methods=['GET', 'POST'])
@permisconst_blueprint.route('/update_permisconst/<status>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def update_permisconst(status=None):
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name
    mun_long = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_long
    mun_lat = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_lat
    permis_id = request.values['type']
    name = request.values['name']
    save = True
    permis_data = Permisconstruct.query.filter_by(id=permis_id).first()
    permis_data = reforme(permis_data.__dict__)
    if not status:
        if len(request.values) > 3:
            if not check_date(request.values['date_depot']):
                flash(u'الرجاء التثبت في صيغة تاريخ التسجيل yyyy/mm/dd', 'warning')
                save = False
            if not check_float(request.values['longitude']):
                flash(u'longitude verified format', 'warning')
                save = False
            if not check_float(request.values['laltitude']):
                flash(u'laltitude verified format', 'warning')
                save = False
            if not check_float(request.values['surface']):
                flash(u'صيغة المساحة خاطئة', 'warning')
                save = False
            if save:
                permis = Permisconstruct.query.get(int(permis_id))
                permis.num_cin = request.values['num_cin']
                permis.nom_titulaire = request.values['nom_titulaire']
                permis.latitude = float(request.values['laltitude'])
                permis.num_demande = request.values['num_demande']
                permis.longitude = float(request.values['longitude'])
                permis.date_depot = request.values['date_depot']
                permis.address = request.values['address']
                permis.desc_construct = request.values['desc_construct']
                permis.surface = request.values['surface']
                permis.type_construct = request.values['type_construct']
                if request.values['permis_status'] in 'refused':
                    permis.date_refuse = request.values['date_refuse']
                    permis.refuse_note = request.values['refuse_note']
                if request.values['permis_status'] in "approved":
                    permis.date_attribution = request.values['date_attribution']
                    permis.date_expiration = request.values['date_expiration']
                    permis.num_permis = request.values['num_permis']
                    permis.mont_total = calculer_montant(float(request.values['surface']))
                db.session.commit()
                flash(u'تم تحيين الرخصة', 'success')
                return redirect(url_for('permis_construction.consult_permisconst'))
    elif 'refuse' in status:
        if 'date_refuse' in request.values:
            if not check_date(request.values['date_refuse']):
                flash(u'تاريخ الرفض مفروض', 'danger')
                save = False
            if save:
                permis = Permisconstruct.query.get(int(permis_id))
                permis.date_refuse = request.values['date_refuse']
                permis.refuse_note = request.values['refuse_note']
                permis.num_permis = None
                permis.date_attribution = None
                permis.date_expiration = None
                permis.mont_total = None
                permis.permis_status = 'refused'
                db.session.commit()
                flash(u'تم تحيين الرخصة', 'success')
                return redirect(url_for('permis_construction.consult_permisconst'))
        return render_template('permis_construction/update_permis.html', permis_id=permis_id, name=name, permis_data=permis_data, mun_name=mun_name, mun_cord=[mun_lat, mun_long], refuse=True)
    elif 'accept' in status:
        if 'date_attribution' in request.values:
            if not check_date(request.values['date_attribution']):
                flash(u'تاريخ اسناد الرخصة مفروض', 'danger')
                save = False
            if not request.values['num_permis'].isdigit():
                flash(u'عدد قرار رخصة البناء مفروض', 'danger')
                save = False
            if save:
                permis = Permisconstruct.query.get(int(permis_id))
                permis.num_permis = request.values['num_permis']
                permis.date_attribution = request.values['date_attribution']
                permis.date_expiration = request.values['date_expiration']
                permis.mont_total = request.values['mont_total']
                permis.date_refuse = None
                permis.refuse_note = None
                permis.permis_status = 'approved'
                db.session.commit()
                flash(u'تم تحيين الرخصة', 'success')
                return redirect(url_for('permis_construction.consult_permisconst'))
        montant_total = int(round(calculer_montant(permis_data['surface'])))
        return render_template('permis_construction/update_permis.html', permis_id=permis_id, name=name, permis_data=permis_data, mun_name=mun_name, mun_cord=[mun_lat, mun_long], accept=True, montant_total=montant_total)
    return render_template('permis_construction/update_permis.html', permis_id=permis_id, name=name, permis_data=permis_data, mun_name=mun_name, mun_cord=[mun_lat, mun_long])


@permisconst_blueprint.route('/refuse_permisconst', methods=['GET', 'POST'])
@login_required
@check_confirmed
def refuse_permisconst():
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name
    mun_long = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_long
    mun_lat = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_lat
    permis_id = request.values['type']
    name = request.values['name']
    permis_data = Permisconstruct.query.filter_by(id=permis_id).first()
    form = PermisrefuseForm()
    if form.validate_on_submit():
        permis = Permisconstruct.query.get(int(permis_id))
        permis.date_refuse = form.date_refuse.data
        permis.permis_status = 'refused'
        db.session.commit()
        flash(u'تم التحيين ', 'success')
        return redirect(url_for('permis_construction.consult_permisconst'))
    else:
        flash(u'الرجاء التثبت فالإستمارة ', 'warning')
    return render_template('permis_construction/form_permis_construction.html', form=form, update=True, accept=False, check=True, permis_id=permis_id, name=name, permis_data=reforme(permis_data.__dict__), mun_name=mun_name, mun_cord=[mun_lat, mun_long])


@permisconst_blueprint.route('/accept_permisconst', methods=['GET', 'POST'])
@login_required
@check_confirmed
def accept_permisconst():
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name
    mun_long = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_long
    mun_lat = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_lat
    permis_id = request.values['type']
    name = request.values['name']
    permis_data = Permisconstruct.query.filter_by(id=permis_id).first()
    form = PermisupdateForm()
    if form.validate_on_submit():
        permis = Permisconstruct.query.get(int(permis_id))
        permis.num_permis = form.num_permis.data
        permis.date_attribution = form.date_attribution.data
        permis.date_expiration = form.date_expiration.data
        permis.mont_charge_fix = form.mont_charge_fix.data
        permis.mont_decision = form.mont_decision.data
        permis.mont_cloture = form.mont_cloture.data
        permis.mont_charge_ascend = form.mont_charge_ascend.data
        permis.mont_total = form.mont_charge_fix.data + form.mont_decision.data + form.mont_cloture.data + form.mont_charge_ascend.data
        permis.permis_status = 'approved'
        db.session.commit()
        flash(u'تم التحيين ', 'success')
        return redirect(url_for('permis_construction.consult_permisconst'))
    else:
        flash(u'الرجاء التثبت فالإستمارة ', 'warning')
    return render_template('permis_construction/form_permis_construction.html', form=form, update=True, accept=True, check=True, permis_id=permis_id, name=name, permis_data=reforme(permis_data.__dict__), mun_name=mun_name, mun_cord=[mun_lat, mun_long])


@permisconst_blueprint.route('/get_files', methods=['GET', 'POST'])
@login_required
@check_confirmed
def get_files():
    confirm_url = url_for('main.home', _external=True) + 'static/files/'
    data = [u.__dict__ for u in Permisconstruct.query.filter_by(municipal_id=current_user.municipal_id).all()]
    encours_list, approved_list, refused_list = [], [], []
    field_refused_list = ['date_refuse']
    field_approved_list = ['date_attribution', 'date_expiration']# , 'montant_charge_fix', 'montant_charge_ascendant', 'montant_cloture', 'montant_decision', 'montant_total']
    for d in data:
        numero_demande = decode_unicode(d['num_demande']) if d['num_demande'] != '' else None
        initial_dict = {'Numero_demande': numero_demande,
                        'Nom_titulaire': decode_unicode(d['nom_titulaire']),
                        'Addresse_travaux': decode_unicode(d['address']),
                        'Description_travaux': decode_unicode(d['desc_construct']),
                        'Longitude': d['longitude'],
                        'Latitude': d['laltitude'],
                        'Date_depot': d['date_depot'].strftime("%Y/%m/%d"),
                        'Type_construction': decode_unicode(d['type_construct'])}
        if request.values['type_file'] == 'en_cours' and d['permis_status'] == 'en_cours':
            ref_encours = 'permis_construction_en_cours' + '_' + current_user.municipal_id
            encours_list.append(initial_dict)
        elif request.values['type_file'] == 'approved' and d['permis_status'] == 'approved':
            ref_approved = 'permis_construction_approuver' + '_' + current_user.municipal_id
            initial_dict['date_attribution'] = d['date_attribution'].strftime("%Y/%m/%d")
            initial_dict['date_expiration'] = d['date_expiration'].strftime("%Y/%m/%d")
            # initial_dict['montant_charge_fix'] = d['mont_charge_fix']
            # initial_dict['montant_charge_ascendant'] = d['mont_charge_ascend']
            # initial_dict['montant_cloture'] = d['mont_cloture']
            # initial_dict['montant_decision'] = d['mont_decision']
            # initial_dict['montant_total'] = d['mont_total']
            approved_list.append(initial_dict)
        elif request.values['type_file'] == 'refused' and d['permis_status'] == 'refused':
            ref_refused = 'permis_construction_refused' + '_' + current_user.municipal_id
            initial_dict['date_refuse'] = d['date_refuse'].strftime("%Y/%m/%d")
            refused_list.append(initial_dict)
    if request.values['type_file'] == 'en_cours':
        if encours_list:
            encour_url = confirm_url + get_csv_file(encours_list, ref_encours, [])
            return render_template('permis_construction/permis_construction.html', data=data, encours=True, encour_url=encour_url)
        else:
            flash(u'ليست هنالك بيانات حول    التراخيص بصدد الدرس', 'warning')
    elif request.values['type_file'] == 'approved':
        if approved_list:
            approved_url = confirm_url + get_csv_file(approved_list, ref_approved, field_approved_list)
            return render_template('permis_construction/permis_construction.html', data=data, approved=True, approved_url=approved_url)
        else:
            flash(u'ليست هنالك بيانات حول    التراخيص المقبولة', 'warning')
    elif request.values['type_file'] == 'refused':
        if refused_list:
            refused_url = confirm_url + get_csv_file(refused_list, ref_refused, field_refused_list)
            return render_template('permis_construction/permis_construction.html', data=data, refused=True, refused_url=refused_url)
        else:
            flash(u'ليست هنالك بيانات حول     التراخيص المرفوضة', 'warning')
    return render_template('permis_construction/permis_construction.html', data=data)


def get_csv_file(data, ref, field_list):
    _ = ['Numero_demande', 'Nom_titulaire', 'Addresse_travaux', 'Date_depot', 'Type_construction', 'Description_travaux', 'Longitude', 'Latitude']
    fieldnames = _ + field_list
    filepath = get_file_path() + ref + '.csv'
    with open(filepath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    return ref + '.csv'


def get_file_path():
    if os.path.isdir('project/static/files/'):
        return 'project/static/files/'
    else:
        return "/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/project/static/files/"


def decode_unicode(v):
    try:
        return v.encode('utf-8')
    except:
        return v


def check_date(date):
    try:
        datetime.datetime.strptime(date, "%Y/%m/%d")
        return True
    except:
        return False


def reforme(p_dict):
    new_dict = {}
    for k, v in p_dict.iteritems():
        if k in ['date_depot', 'date_refuse', 'date_expiration', 'date_attribution'] and v:
            new_dict[k] = v.strftime("%Y/%m/%d")
        else:
            new_dict[k] = v
    return new_dict


def check_float(value):
    try:
        float(value)
        return True
    except:
        return False


def calculer_montant(surface):
    if surface < 101:
        montant = 15000 + (surface * 100)
    elif surface < 201:
        montant = 60000 + (surface * 300)
    elif surface < 301:
        montant = 120000 + (surface * 400)
    elif surface < 401:
        montant = 300000 + (surface * 600)
    else:
        montant = 750000 + (surface * 1000)
    return montant