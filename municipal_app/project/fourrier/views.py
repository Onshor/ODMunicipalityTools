# project/fourrier/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from .forms import FourrierForm, DetentionForm, ReleaseForm
from project.models import Fourrier, Detention
from project import db
import datetime
from pprint import pprint as pp

################
#### config ####
################

fourrier_blueprint = Blueprint('fourrier', __name__,)


################
#### routes ####
################

@fourrier_blueprint.route('/add_fourrier', methods=['GET', 'POST'])
@login_required
@check_confirmed
def add_fourrier():
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
    return render_template('fourrier/form_fourrier.html', form=form, update=False)


@fourrier_blueprint.route('/add_detention', methods=['GET', 'POST'])
@login_required
@check_confirmed
def add_detention():
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
    fourrier_data = [u.__dict__ for u in Fourrier.query.filter_by(municipal_id=current_user.municipal_id).all()]
    detention_data = [u.__dict__ for u in Detention.query.filter_by(municipal_id=current_user.municipal_id).all()]
    return render_template('fourrier/fourrier.html', fourrier_data=fourrier_data, detention_data=reforme_list(detention_data))


@fourrier_blueprint.route('/update_fourrier', methods=['GET', 'POST'])
@login_required
@check_confirmed
def update_fourrier():
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
    return render_template('fourrier/form_fourrier.html', update=True, fourrier_data=fourrier_data)


@fourrier_blueprint.route('/update_detention', methods=['GET', 'POST'])
@login_required
@check_confirmed
def update_detention():
    detention_data = Detention.query.filter_by(id=request.values['d_id']).first().__dict__
    save = True
    name_fourrier_option = [(str(row.id), row.Name_Fourrier) for row in Fourrier.query.filter_by(municipal_id=current_user.municipal_id).all()]
    authority_option = [(u'الشرطة البيئية', u'الشرطة البيئية'), (u'الشرطة البلدية', u'الشرطة البلدية'), (u'البلدية', u'البلدية'), (u'شرطة المرور', u'شرطة المرور'), (u'الحرس الوطني', u'الحرس الوطني')]
    if len(request.values) > 3:
        if not check_date(request.values['Date_Detention']):
            flash(u'Date_Detention verified format', 'warning')
            save = False
        if save:
            detent = Detention.query.get(int(request.values['d_id']))
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
