# project/fourrier/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from .forms import FourrierForm, DetentionForm, ReleaseForm
from project.models import Fourrier, Detention, Municipality, Data_Publisher
from project import db
from project.util import save_auto_update, push_api, get_auto_update_data, decode_pub_data
import datetime
from project.util import check_role
import csv
import os

################
#### config ####
################

fourrier_blueprint = Blueprint('fourrier', __name__,)
module_id = 3

################
#### routes ####
################


@fourrier_blueprint.route('/add_fourrier', methods=['GET', 'POST'])
@login_required
@check_confirmed
def add_fourrier():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name
    mun_long = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_long
    mun_lat = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_lat
    form = FourrierForm(request.form)
    if form.validate_on_submit():
        fourrier = Fourrier(
            user_id=current_user.id,
            municipal_id=current_user.municipal_id,
            Name_Fourrier=form.Name_Fourrier.data,
            Address_Fourrier=form.Address_Fourrier.data,
            Longitude=form.Longitude.data,
            Laltitude=form.Laltitude.data
            )
        db.session.add(fourrier)
        db.session.commit()
        flash(u'تم حفظها في قاعدة البيانات', 'success')
        return redirect(url_for('fourrier.fourrier'))
    return render_template('fourrier/form_fourrier.html', form=form, update=False, mun_name=mun_name, mun_cord=[mun_lat, mun_long])


@fourrier_blueprint.route('/add_detention', methods=['GET', 'POST'])
@login_required
@check_confirmed
def add_detention():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    form = DetentionForm(request.form)
    form.Name_Fourrier2.choices = [(None, '')]
    form.Name_Fourrier2.choices.extend([(str(row.id), row.Name_Fourrier) for row in Fourrier.query.filter_by(municipal_id=current_user.municipal_id).all()])
    if form.validate_on_submit():
        detention = Detention(
            user_id=current_user.id,
            municipal_id=current_user.municipal_id,
            Date_Detention=form.Date_Detention.data,
            Cause_Detention=form.Cause_Detention.data,
            Descr_Detention=form.Descr_Detention.data,
            Name_Owner=form.Name_Owner.data,
            Authority_Detention=form.Authority_Detention.data,
            Type_Detention=form.Type_Detention.data,
            fourrier_id=int(form.Name_Fourrier2.data),
            Name_Fourrier=Fourrier.query.filter_by(id=int(form.Name_Fourrier2.data)).first().Name_Fourrier,
            Registration_Detention=form.Registration_Detention.data,
            Num_Bon=None,
            Date_Release=None,
            Note=None,
            Status_Detention=u'محجوز')
        db.session.add(detention)
        db.session.commit()
        flash(u'تم حفظها في قاعدة البيانات', 'success')
        return redirect(url_for('fourrier.fourrier'))
    return render_template('fourrier/form_detention.html', form=form)


@fourrier_blueprint.route('/fourrier', methods=['GET', 'POST'])
@login_required
@check_confirmed
def fourrier():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    fourrier_data = [u.__dict__ for u in Fourrier.query.filter_by(municipal_id=current_user.municipal_id).all()]
    detention_data = [u.__dict__ for u in Detention.query.filter_by(municipal_id=current_user.municipal_id).all()]
    if 'delete_row' in request.values:
        if request.values['delete_row'] == 'delete_row_detention':
            det = Detention.query.get(int(request.values['type']))
            flash(u'تم فسخ المحجوز', 'success')
        elif Detention.query.filter_by(fourrier_id=int(request.values['type'])).first():
            flash(u'لا يمكن فسخ المستودع وبه محجوز', 'warning')
            return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data), msg='yooo')
        else:
            det = Fourrier.query.get(int(request.values['type']))
            flash(u'تم فسخ المستودع', 'success')
        db.session.delete(det)
        db.session.commit()
        return redirect(url_for('fourrier.fourrier'))
    return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data))


@fourrier_blueprint.route('/update_fourrier', methods=['GET', 'POST'])
@login_required
@check_confirmed
def update_fourrier():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name
    mun_long = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_long
    mun_lat = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_lat
    fourrier_data = Fourrier.query.filter_by(id=request.values['f_id']).first().__dict__
    save = True
    if len(request.values) > 3:
        if not check_float(request.values['Longitude']):
            flash(u'longitude verified format', 'warning')
            save = False
        if not check_float(request.values['Laltitude']):
            flash(u'laltitude verified format', 'warning')
            save = False
        if save:
            four = Fourrier.query.get(int(request.values['f_id']))
            four.Longitude = float(request.values['Longitude'])
            four.Laltitude = float(request.values['Laltitude'])
            four.Name_Fourrier = request.values['Name_Fourrier']
            four.Address_Fourrier = request.values['Address_Fourrier']
            db.session.commit()
            Detention.query.filter_by(municipal_id=current_user.municipal_id, fourrier_id=int(request.values['f_id'])).update(dict(Name_Fourrier=request.values['Name_Fourrier']))
            db.session.commit()
            flash(u'تم تحيين مستودع الحجز', 'success')
            return redirect(url_for('fourrier.fourrier'))
    return render_template('fourrier/form_fourrier.html', update=True, fourrier_data=fourrier_data, mun_name=mun_name, mun_cord=[mun_lat, mun_long])


@fourrier_blueprint.route('/update_detention', methods=['GET', 'POST'])
@login_required
@check_confirmed
def update_detention():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    detention_data = Detention.query.filter_by(id=request.values['d_id']).first().__dict__
    save = True
    name_fourrier_option = [(str(row.id), row.Name_Fourrier) for row in Fourrier.query.filter_by(municipal_id=current_user.municipal_id).all()]
    authority_option = [(u'الشرطة البيئية', u'الشرطة البيئية'), (u'الشرطة البلدية', u'الشرطة البلدية'), (u'البلدية', u'البلدية'), (u'شرطة المرور', u'شرطة المرور'), (u'الحرس الوطني', u'الحرس الوطني'), (u'عدل منفذ', u'عدل منفذ'), (u' حرس المرور', u' حرس المرور')]
    if len(request.values) > 3:
        if not check_date(request.values['Date_Detention']):
            flash(u'Date_Detention verified format', 'warning')
            save = False
        if save:
            detent = Detention.query.get(int(request.values['d_id']))
            detent.Descr_Detention = request.values['Descr_Detention']
            detent.Date_Detention = request.values['Date_Detention']
            detent.Cause_Detention = request.values['Cause_Detention']
            detent.Name_Owner = request.values['Name_Owner']
            detent.Authority_Detention = request.values['Authority_Detention']
            detent.Type_Detention = request.values['Type_Detention']
            detent.Registration_Detention = request.values['Registration_Detention']
            detent.fourrier_id = int(request.values['fourrier_id'])
            detent.Name_Fourrier = Fourrier.query.filter_by(id=int(request.values['fourrier_id'])).first().Name_Fourrier
            db.session.commit()
            flash(u'تم تحيين مستودع الحجز', 'success')
            return redirect(url_for('fourrier.fourrier'))
    return render_template('fourrier/form_detention.html', update=True, detention_data=reforme_dict(detention_data), name_fourrier_option=name_fourrier_option, authority_option=authority_option)


@fourrier_blueprint.route('/get_fourrier_file/api', methods=['GET', 'POST'])
@login_required
@check_confirmed
def api():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    push_api(request.values)
    fourrier_data = [u.__dict__ for u in Fourrier.query.filter_by(municipal_id=current_user.municipal_id).all()]
    detention_data = [u.__dict__ for u in Detention.query.filter_by(municipal_id=current_user.municipal_id).all()]
    return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data))


@fourrier_blueprint.route('/get_fourrier_file', methods=['GET', 'POST'])
@login_required
@check_confirmed
def get_fourrier_file():
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    confirm_url = url_for('main.home', _external=True) + 'static/files/'
    fourrier_file, detention_file = [], []
    fourrier_data = [u.__dict__ for u in Fourrier.query.filter_by(municipal_id=current_user.municipal_id).all()]
    detention_data = [u.__dict__ for u in Detention.query.filter_by(municipal_id=current_user.municipal_id).all()]
    if 'type_file' in request.values:
        if request.values['type_file'] == 'list_fourrier':
            for f in fourrier_data:
                f_data, f_fieldnames = get_file_content(f, 'fourriere')
                fourrier_file.append(f_data)
            ref = 'list_fourrierre_' + str(current_user.municipal_id)
            fourrier_f = get_csv_file(fourrier_file, ref, f_fieldnames)
            save_auto_update(fourrier_f, 'Fourriere')
            fourrier_url = confirm_url + fourrier_f
            f_data = get_auto_update_data({'file_name': fourrier_f, 'link': fourrier_url, 'type': 'fourriere'})
            return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data), f_data=f_data, fourrier_lancher=True)
        if request.values['type_file'] == 'list_archive':
            for d in detention_data:
                if u'محجوز' not in d['Status_Detention']:
                    det_lon = Fourrier.query.filter_by(id=d['fourrier_id']).first().Longitude
                    det_lat = Fourrier.query.filter_by(id=d['fourrier_id']).first().Laltitude
                    detention_file.append({'Longitude': det_lon,
                                           'Latitude': det_lat,
                                           'Lieu_fourriere': decode_unicode(d['Name_Fourrier']),
                                           'Date_enlevement': d['Date_Detention'].strftime("%Y/%m/%d"),
                                           'Cause_enlevement': decode_unicode(d['Cause_Detention']),
                                           'Nom_proprietaire': decode_unicode(d['Name_Owner']),
                                           'Autorite_origine_de_detention': decode_unicode(d['Authority_Detention']),
                                           'Type_objets_detenues': decode_unicode(d['Type_Detention']),
                                           'Imatriculation': decode_unicode(d['Registration_Detention']),
                                           'Desc_objets_detenues': decode_unicode(d['Descr_Detention']),
                                           'Date_restitution': d['Date_Release'],
                                           'Num_recu': d['Num_Bon'],
                                           'Amende': d['montant_sortie']})
            if detention_file:
                ref = 'list_archive_' + str(current_user.municipal_id)
                field_list = ['Date_enlevement', 'Cause_enlevement', 'Autorite_origine_de_detention', 'Nom_proprietaire', 'Type_objets_detenues', 'Imatriculation', 'Desc_objets_detenues', 'Lieu_fourriere', 'Longitude', 'Latitude', 'Date_restitution', 'Num_recu', 'Amende']
                detention_f = get_csv_file(detention_file, ref, field_list)
                save_auto_update(detention_f, 'Fourriere')
                detention_url = confirm_url + detention_f
                d_data = get_auto_update_data({'file_name': detention_f, 'link': detention_url, 'type': 'detention'})
                return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data), d_data=d_data, archive_lancher=True)
            else:
                flash(u'ليس هنالك بيانات ', 'info')
        else:
            for d in detention_data:
                if u'محجوز' in d['Status_Detention']:
                    det_lon = Fourrier.query.filter_by(id=d['fourrier_id']).first().Longitude
                    det_lat = Fourrier.query.filter_by(id=d['fourrier_id']).first().Laltitude
                    d_data, d_fieldnames = get_file_content(d, 'detention')
                    d_fieldnames.extend(['Longitude', 'Latitude'])
                    d_data['Longitude'] = det_lon
                    d_data['Latitude'] = det_lat
                    detention_file.append(d_data)
            if detention_file:
                ref = 'list_detention_' + str(current_user.municipal_id)
                detention_f = get_csv_file(detention_file, ref, d_fieldnames)
                save_auto_update(detention_f, 'Fourriere')
                detention_url = confirm_url + detention_f
                d_data = get_auto_update_data({'file_name': detention_f, 'link': detention_url, 'type': 'detention'})
                return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data), d_data=d_data, detention_lancher=True)
            else:
                flash(u'ليس هنالك بيانات ', 'info')
    return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data))


@fourrier_blueprint.route('/update_detention/archiver/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def archiver_fourrier(id):
    if not check_role(module_id):
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))
    form = ReleaseForm(request.form)
    if form.validate_on_submit():
        det = Detention.query.get(int(id))
        det.Status_Detention = u'أرشيف'
        det.montant_sortie = form.montant_sortie.data
        det.Date_Release = form.Date_Release.data
        det.Note = form.Note.data
        db.session.commit()
        flash(u'تم تحيين', 'success')
        return redirect(url_for('fourrier.fourrier'))
    return render_template('fourrier/archiver.html', form=form)


def get_csv_file(data, ref, field_list):
    filepath = get_file_path() + ref + '.csv'
    with open(filepath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=field_list)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    return ref + '.csv'


def get_file_content(d, types):
    data_pub = Data_Publisher.query.filter_by(municipal_id=current_user.municipal_id, modules_id=module_id).first().data_pub
    pub_dict, fieldnames = {}, []
    for p in data_pub:
        if p['type'] == types:
            for e in p['pub']:
                if e['status']:
                    fieldnames.append(e['pub_name'])
                    pub_dict[e['pub_name']] = decode_pub_data(d[e['db_name']])
    return pub_dict, fieldnames


def get_file_path():
    if os.path.isdir('project/static/files/'):
        return 'project/static/files/'
    else:
        return "/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/project/static/files/"


def get_file_content_fourrier(d):
    return 0


def check_float(value):
    try:
        float(value)
        return True
    except:
        return False


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


def reforme_list(p_list):
    new_list = []
    for d in p_list:
        new_list.append(reforme_dict(d))
    return new_list


def reforme_dict(d_dict):
    new_dict = {}
    for k, v in d_dict.iteritems():
        if k in ['Date_Detention'] and v:
            new_dict[k] = v.strftime("%Y/%m/%d")
        else:
            new_dict[k] = v
    return new_dict
