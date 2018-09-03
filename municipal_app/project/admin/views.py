# project/admin/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project.models import User, Municipality
from .forms import ChangePwdForm, AddmunForm
from project import db, bcrypt
import ckanapi
from pprint import pprint as pp


################
#### config ####
################


admin_blueprint = Blueprint('admin', __name__,)


@admin_blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
@check_confirmed
def admin():
    if 'deleting' in request.values:
        mun_id = request.values['id']
        mun = User.query.get(str(mun_id))
        mun.deleted = True
        db.session.commit()
        flash(u'تم حذف المستخدم','success')
        return redirect(url_for('admin.admin'))
    if 'activer' in request.values:
        user_id = request.values['id']
        user = User.query.get(int(user_id))
        user.confirmed = True
        db.session.commit()
        return redirect(url_for('admin.admin'))
    elif 'cancel_user' in request.values:
        user_id = request.values['id']
        user = User.query.get(int(user_id))
        user.activate = False
        db.session.commit()
        return redirect(url_for('admin.admin'))
    if 'activate_user' in request.values:
        user_id = request.values['id']
        user = User.query.get(int(user_id))
        if user.confirmed:
            user.activate = True
            db.session.commit()
        else:
            flash(u'هذا المستعمل غير معتمد ، الرجاء اعتماده قبل تفعيله','warning')
        return redirect(url_for('admin.admin'))
    new_list = []
    list_user = [u.__dict__ for u in User.query.all()]
    for u in list_user:
        if not u['deleted'] and int(u['municipal_id']) != 1:
            mun_name_ar = Municipality.query.filter_by(municipal_id=u['municipal_id']).first().municipal_name_ar  if int(u['municipal_id']) != 1 else 'Super Admin'
            mun_name = mun_name_ar + ' ' + Municipality.query.filter_by(municipal_id=u['municipal_id']).first().municipal_name  if int(u['municipal_id']) != 1 else 'Super Admin'
            new_list.append({'confirmed': u['confirmed'],
                             'confirmed_on': u['confirmed_on'].strftime("%d/%m/%Y") if u['confirmed'] and u['confirmed_on'] else None,
                             'name': u['name'],
                             'id': u['id'],
                             'email': u['email'],
                             'last_name': u['last_name'],
                             'municipal_id': u['municipal_id'],
                             'municipality': mun_name,
                             'register_on': u['registered_on'].strftime("%d/%m/%Y"),
                             'last_login': u['last_login'] if u['last_login'] else '',
                             'activate': u['activate'],
                             'admin': u['admin'],
                             'municipal_admin': u['municipal_admin'],
                             'phone_number': u['phone_number'] if u['phone_number'] else '',
                             'work_position': u['work_position'] if u['work_position'] else ''})
    return render_template('admin/admin.html', list_user=new_list)


@admin_blueprint.route('/admin/editpwd/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_pawd_admin(id):
    if current_user.admin or current_user.municipal_admin:
        form = ChangePwdForm()
        user = User.query.filter_by(id=int(id)).first().__dict__
        mun = Municipality.query.filter_by(municipal_id=str(user['municipal_id'])).first()
        mun = mun.municipal_name_ar
        if form.validate_on_submit():
            user_admin = User.query.filter_by(email=current_user.email).first()
            if user_admin and bcrypt.check_password_hash(user_admin.password, request.form['admin_password']):
                user = User.query.filter_by(id=int(id)).first()
                if user:
                    user.password = bcrypt.generate_password_hash(form.password.data)
                    db.session.commit()
                    flash(u'تم تغير كلمة السر بنجاح', 'success')
                    return redirect(url_for('admin.admin'))
                else:
                    flash(u'تغير كلمة السر لم ينجح', 'danger')
                    return render_template('admin/edit_pwd_admin.html', form=form, user=user, mun=mun)
            else:
                flash(u'تحقق من  كلمة السر', 'danger')
                return render_template('admin/edit_pwd_admin.html', form=form, user=user, mun=mun)
        return render_template('admin/edit_pwd_admin.html', form=form, user=user, mun=mun)
    else:
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))


@admin_blueprint.route('/admin/admin_mun', methods=['GET', 'POST'])
@login_required
@check_confirmed
def admin_mun():
    new_list = []
    if current_user.admin:
        if 'mun_act' in request.values:
            mun_id = request.values['id']
            mun = Municipality.query.get(str(mun_id))
            mun_name_ar = Municipality.query.filter_by(municipal_id=str(mun_id)).first().municipal_name_ar
            mun_name_fr = Municipality.query.filter_by(municipal_id=str(mun_id)).first().municipal_name
            mun.approved = True
            api_dict = {"name" : mun_name_fr.lower().replace(' ','_').replace(u'\u200e', '').replace(u'\xe9', '') + '_01', "title": u'بلدية ' + mun_name_ar}
            if not Municipality.query.filter_by(municipal_id=str(mun_id)).first().ckan_id:
                pp(api_dict)
                api = create_organization_ckan(api_dict)
                mun.ckan_id = api['id']
            db.session.commit()
            flash(u'تم إضافة بلدية' + mun_name_ar + u' إلى موقعين','success')
            return redirect(url_for('admin.admin_mun'))
        if 'mun_dact' in request.values:
            mun_id = request.values['id']
            mun = Municipality.query.get(str(mun_id))
            mun_name = Municipality.query.filter_by(municipal_id=str(mun_id)).first().municipal_name_ar
            mun.approved = False
            db.session.commit()
            flash(u'تم سحب بلدية' + mun_name + u' من موقعين','success')
            return redirect(url_for('admin.admin_mun'))
        if 'deleting' in request.values:
            mun_id = request.values['id']
            mun = Municipality.query.get(str(mun_id))
            mun.deleted = True
            db.session.commit()
            flash(u'تم حذف البلدية','success')
            return redirect(url_for('admin.admin_mun'))
        list_mun = [u.__dict__ for u in Municipality.query.all() if int(u.municipal_id) > 1]
        for x in list_mun:
            if not x['deleted']:
                dict_m = x
                dict_m['search_name'] = x['municipal_name_ar'] + ' ' + x['municipal_name']
                new_list.append(dict_m)
        list_names = [_['municipal_name_ar'] + ' ' + _['municipal_name'] for _ in list_mun]
        list_states = list(set([_['municipal_state'] for _ in list_mun]))
        new_list = sorted(new_list, key=lambda k: (-k["approved"], k['municipal_id']))
        return render_template('admin/admin_mun.html', list_mun=new_list, list_states=sorted(list_states), list_names=sorted(list_names))
    else:
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))



@admin_blueprint.route('/admin/mun/edit/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_admin_mun(id):
    if current_user.admin:
        if 'edit' in request.values:
            save = True
            if not check_float(request.values['municipal_lat']):
                flash(u'longitude verified format', 'warning')
                save = False
            if not check_float(request.values['municipal_long']):
                flash(u'laltitude verified format', 'warning')
                save = False
            if save:
                mun = Municipality.query.get(str(request.values['id']))
                mun.municipal_name = request.values['municipal_name']
                mun.municipal_name_ar = request.values['municipal_name_ar']
                mun.municipal_long = request.values['municipal_long']
                mun.municipal_lat = request.values['municipal_lat']
                db.session.commit()
                flash(u'لقد تم التحيين بنجاح ', 'success')
                return redirect(url_for('admin.admin_mun'))
        data = Municipality.query.filter_by(municipal_id=str(id)).first()
        return render_template('admin/edit_mun.html', data=data)
    else:
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))


@admin_blueprint.route('/admin/user/edit/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_admin_user(id):
    save = True
    if current_user.admin or current_user.municipal_admin:
        data = User.query.filter_by(id=int(id)).first()
        if 'edit' in request.values:
            if check_string(request.values['name']) and check_string(request.values['last_name']):
                if  not check_email(request.values['email']):
                    save = False
                    flash(u'صيغة البريد الالكتروني غير صحيحة', 'danger')
                if not mail_exist(request.values['email'], data.email):
                    save = False
                    flash(u'البريد الإلكتروني موجود', 'danger')
                if save:
                    user = User.query.get(int(request.values['id']))
                    user.name = request.values['name']
                    user.admin = get_role(request.values['role'])['admin']
                    user.municipal_admin = get_role(request.values['role'])['municipal_admin']
                    user.last_name = request.values['last_name']
                    user.municipal_id = request.values['municipal_id']
                    user.email = request.values['email']
                    user.work_position = request.values['work_position'] if request.values['work_position'] else None
                    user.phone_number = request.values['phone_number'] if request.values['phone_number'] else None
                    db.session.commit()
                    flash(u'لقد تم التحيين بنجاح ', 'success')
                    return redirect(url_for('admin.admin'))
            else:
                flash(u'تحقق من الاسم واللقب', 'warning')
        data = User.query.filter_by(id=int(id)).first() 
        list_mun = [u.__dict__ for u in Municipality.query.all() if int(u.municipal_id) > 1]
        data_mun = [{'value':_['municipal_id'], 'name':_['municipal_name'] + ' ' + _['municipal_name_ar']} for _ in list_mun if _['approved'] and not _['deleted']]
        mun = Municipality.query.filter_by(municipal_id=str(data.municipal_id)).first()
        user_mun_name = mun.municipal_name + ' ' + mun.municipal_name_ar
        return render_template('admin/edituser.html', data=data, data_mun=data_mun, user_mun_name=user_mun_name)
    else:
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))


@admin_blueprint.route('/admin/add_mun', methods=['GET', 'POST'])
@login_required
@check_confirmed
def add_admin_mun():
    form = AddmunForm()
    if form.validate_on_submit():
        db.session.add(Municipality(
            municipal_id=str(form.municipal_id.data),
            municipal_name=form.municipal_name.data,
            municipal_state=form.municipal_state.data,
            municipal_long=form.municipal_long.data,
            municipal_lat=form.municipal_lat.data,
            municipal_name_ar=form.municipal_name_ar.data,
            approved=True if form.approved.data in 'signed' else False,
            deleted=False))
        db.session.commit()
        return redirect(url_for('admin.admin_mun'))
    return render_template('admin/add_mun.html', form=form)


def get_role(role):
    if int(role) == 0:
        return {'admin': True, 'municipal_admin': False}
    elif int(role) == 1:
        return {'admin': False, 'municipal_admin': True}
    else:
        return {"admin": False, 'municipal_admin': False} 


def check_string(v):
    if not v or v.strip() == '':
        return False
    else:
        return True

def check_float(value):
    try:
        float(value)
        return True
    except:
        return False

def check_email(mail):
    if '@' in mail and '.' in mail:
        return True
    else:
        return False

def mail_exist(mail, user_email):
    email_list = [_.email for _ in User.query.filter(User.email != user_email).all()]
    if mail in email_list:
        return False
    else:
        return True


def create_organization_ckan(data):
    ckan = ckanapi.RemoteCKAN('http://openbaladiati.tn/', apikey='545dd248-0887-47c5-ae65-248c2772a53b')
    b = ckan.action.organization_create(**data)
    return b