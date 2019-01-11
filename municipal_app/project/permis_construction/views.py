# project/permis_construction/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from project.models import Permisconstruct, Municipality, Data_Publisher, Packages
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from .forms import PermisencourForm, PermisrefuseForm, PermisupdateForm
from project.util import save_auto_update, push_api, get_auto_update_data
from project import db
from project.ckan_api import module_publisher
from project.util import check_role, decode_pub_data
import os
import datetime
import csv


################
#### config ####
################

permisconst_blueprint = Blueprint('permis_construction', __name__,)
module_id = 2

################
#### routes ####
################


@permisconst_blueprint.route('/permisconst', methods=['GET', 'POST'])
@login_required
@check_confirmed
def permisconst():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
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
                                 refuse_note=None,
                                 nom_architect=form.nom_architect.data
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
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    if 'approved' in request.values:
        p_id = Permisconstruct.query.get(int(request.values['type']))
        p_id.reserve_note = None
        p_id.permis_status = 'approved'
        db.session.commit()
        flash(u'تم تغير وضعية الرخصة إلى مقبولة ', 'success')
        return redirect(url_for('permis_construction.consult_permisconst'))
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
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
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
            if not request.values['nom_architect'].strip():
                flash(u'إسم المهندس المعماري إجباري', 'warning')
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
                permis.nom_architect = request.values['nom_architect']
                if request.values['permis_status'] in 'refused':
                    permis.date_refuse = request.values['date_refuse']
                    permis.refuse_note = request.values['refuse_note']
                if request.values['permis_status'] in "approved":
                    permis.date_attribution = request.values['date_attribution']
                    permis.date_expiration = request.values['date_expiration']
                    permis.num_permis = request.values['num_permis']
                    permis.mont_total = calculer_montant(float(request.values['surface']))
                if request.values['permis_status'] == "approved_with":
                    permis.reserve_note = request.values['reserve_note']
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
                permis.reserve_note = None
                permis.permis_status = 'refused'
                db.session.commit()
                flash(u'تم تحيين الرخصة', 'success')
                return redirect(url_for('permis_construction.consult_permisconst'))
        return render_template('permis_construction/update_permis.html', permis_id=permis_id, name=name, permis_data=permis_data, mun_name=mun_name, mun_cord=[mun_lat, mun_long], refuse=True)
    elif 'accept' in status:
        if 'with' in status:
            approved_with = True
        else:
            approved_with = False
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
                if approved_with:
                    permis.permis_status = 'approved_with'
                    permis.reserve_note = request.values['reserve_note']
                else:
                    permis.permis_status = 'approved'
                    permis.reserve_note = None
                db.session.commit()
                flash(u'تم تحيين الرخصة', 'success')
                return redirect(url_for('permis_construction.consult_permisconst'))
        montant_total = int(round(calculer_montant(permis_data['surface'])))
        return render_template('permis_construction/update_permis.html', permis_id=permis_id, name=name, permis_data=permis_data, mun_name=mun_name, mun_cord=[mun_lat, mun_long], accept=True, montant_total=montant_total, approved_with=approved_with)
    return render_template('permis_construction/update_permis.html', permis_id=permis_id, name=name, permis_data=permis_data, mun_name=mun_name, mun_cord=[mun_lat, mun_long])


@permisconst_blueprint.route('/refuse_permisconst', methods=['GET', 'POST'])
@login_required
@check_confirmed
def refuse_permisconst():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
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
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
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


@permisconst_blueprint.route('/get_files/api', methods=['GET', 'POST'])
@login_required
@check_confirmed
def api():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    push_api(request.values)
    data = [u.__dict__ for u in Permisconstruct.query.filter_by(municipal_id=current_user.municipal_id).all()]
    return render_template('permis_construction/permis_construction.html', data=data)


@permisconst_blueprint.route('/get_files', methods=['GET', 'POST'])
@login_required
@check_confirmed
def get_files():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    data_pub = Data_Publisher.query.filter_by(municipal_id=current_user.municipal_id, modules_id=module_id).first().data_pub
    data = [u.__dict__ for u in Permisconstruct.query.filter_by(municipal_id=current_user.municipal_id).all()]
    if data:
        files_data = [get_permis_files(data, 'en_cours', data_pub, u'ملف الرخص بصدد الدرس')]
        files_data.append(get_permis_files(data, 'approved', data_pub, u'ملف الرخص المقبولة'))
        files_data.append(get_permis_files(data, 'refused', data_pub, u'ملف الرخص المرفوضة'))
        create = Packages.query.filter_by(modules_id=str(module_id), package_type='permis_de_construction', municipal_id=current_user.municipal_id).first()
        if 'open_api' in request.values:
            module_publisher(module_id, 'permis_de_construction', files_data, '', '', '')
            create = Packages.query.filter_by(modules_id=str(module_id), package_type='permis_de_construction', municipal_id=current_user.municipal_id).first()
            return redirect(url_for('permis_construction.consult_permisconst'))
        return render_template('permis_construction/permis_construction.html', data=data, file=True, files_data=files_data, create=create)
    else:
        flash(u'ليست هنالك بيانات', 'warning')
    return render_template('permis_construction/permis_construction.html', data=data)


def get_permis_files(data, permis_status, data_pub, text_head):
    pub_list, fieldnames = [], []
    confirm_url = url_for('main.home', _external=True) + 'static/files/'
    for d in data:
        if permis_status in d['permis_status']:
            pub_dict = {}
            for item in data_pub:
                if permis_status == item['type']:
                    for p in item['pub']:
                        if p['status']:
                            fieldnames.append(p['pub_name'])
                            pub_dict[p['pub_name']] = decode_pub_data(d[p['db_name']])
            pub_list.append(pub_dict)
    file_name = 'permis_construction_' + permis_status + '_' + current_user.municipal_id
    file_name = get_csv_file(pub_list, file_name, list(set(fieldnames)))
    save_auto_update(file_name, 'Permis du construction')
    file_url = confirm_url + file_name
    file_data = get_auto_update_data({'file_name': file_name, 'link': file_url, 'type': 'pc_' + permis_status})
    file_data['text_head'] = text_head
    return file_data


def get_csv_file(data, ref, fieldnames):
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