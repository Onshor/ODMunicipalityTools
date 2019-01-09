# project/admin/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project.models import User, Municipality, Modules, Users_Models, Data_Publisher
from .forms import ChangePwdForm, AddmunForm
from project import db, bcrypt, app
from project.email import send_admin_email, send_confirm_email
import ckanapi
import json
import unidecode
import time
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
        user.activate = True
        add_role_user(user)
        db.session.commit()
        flash(u'تم إعتماد و تفعيل حساب ' + user.name + ' ' + user.last_name,'success')
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
    list_user = [u.__dict__ for u in User.query.all()] if current_user.admin else [u.__dict__ for u in User.query.filter_by(municipal_id=current_user.municipal_id).all()]
    for u in list_user:
        if not u['deleted'] and int(u['municipal_id']) != 1:
            list_id = [_.modules_id for _ in Users_Models.query.filter_by(user_id=u['id']).all()]
            roles = ' ,'.join([Modules.query.get(i).name_ar for i in list_id])
            mun_name_ar = Municipality.query.filter_by(municipal_id=u['municipal_id']).first().municipal_name_ar  if int(u['municipal_id']) != 1 else 'Super Admin'
            mun_name = mun_name_ar + ' ' + Municipality.query.filter_by(municipal_id=u['municipal_id']).first().municipal_name  if int(u['municipal_id']) != 1 else 'Super Admin'
            new_list.append({'confirmed': u['confirmed'],
                             'confirmed_on': u['confirmed_on'].strftime("%d/%m/%Y") if u['confirmed'] and u['confirmed_on'] else None,
                             'name': u['name'],
                             'roles': roles, 
                             'id': u['id'],
                             'email': u['email'],
                             'last_name': u['last_name'],
                             'municipal_id': u['municipal_id'],
                             'municipality': mun_name,
                             'register_on': u['registered_on'].strftime("%d/%m/%Y"),
                             'last_login': u['last_login'] if u['last_login'] else None,
                             'activate': u['activate'],
                             'admin': u['admin'],
                             'municipal_admin': u['municipal_admin'],
                             'phone_number': u['phone_number'] if u['phone_number'] else '',
                             'work_position': u['work_position'] if u['work_position'] else ''})
    return render_template('admin/admin.html', list_user=sorted(new_list,key=lambda k: k["last_login"], reverse=True))


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
            if not Municipality.query.filter_by(municipal_id=str(mun_id)).first().ckan_id:
                name = unidecode.unidecode(mun_name_fr).lower().replace(' ','_')
                try:
                    if name in get_ckan_organization_list():
                        api_name = unidecode.unidecode(mun_name_fr).lower().replace(' ','_') + '_01'
                    else:
                        api_name = unidecode.unidecode(mun_name_fr).lower().replace(' ','_')
                    api_dict = {"name" : api_name, "title": u'بلدية ' + mun_name_ar}
                    api = create_organization_ckan(api_dict)
                except:
                    api_dict = {"name" : unidecode.unidecode(mun_name_fr).lower().replace(' ','_') + '_0001', "title": u'بلدية ' + mun_name_ar}
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
    save, list_modules_user = True, []
    if current_user.admin or (current_user.municipal_admin and current_user.municipal_id == User.query.get(int(id)).municipal_id):
        data = User.query.filter_by(id=int(id)).first()
        list_modules = [m.__dict__ for m in Modules.query.all()]
        for r in list_modules:
            if Users_Models.query.filter_by(user_id=int(id), modules_id=int(r['id'])).first():
                r.update({'role': True})
            else:
                r.update({'role': False})
            list_modules_user.append(r)
        if 'edit' in request.values:
            if check_string(request.values['name']) and check_string(request.values['last_name']):
                if  not check_email(request.values['email']):
                    save = False
                    flash(u'صيغة البريد الالكتروني غير صحيحة', 'danger')
                if not mail_exist(request.values['email'], data.email):
                    save = False
                    flash(u'البريد الإلكتروني موجود', 'danger')
                if save:
                    get_role(request, int(id))
                    user = User.query.get(int(request.values['id']))
                    user.name = request.values['name']
                    user.admin = get_post(request.values['fonction'])['admin']
                    user.municipal_admin = get_post(request.values['fonction'])['municipal_admin']
                    user.last_name = request.values['last_name']
                    user.municipal_id = request.values['municipal_id'] if current_user.admin else user.municipal_id
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
        return render_template('admin/edituser.html', data=data, data_mun=data_mun, user_mun_name=user_mun_name, list_modules=list_modules_user)
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


@admin_blueprint.route('/admin/data_publisher/<status>', methods=['GET', 'POST'])
@admin_blueprint.route('/admin/data_publisher/<status>/<types>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def data_publisher(status, types=None):
    if status == 'permis':
        list_item = Data_Publisher.query.filter_by(modules_id=2, municipal_id=current_user.municipal_id).first().__dict__
        data_id = list_item['id']
        for t in list_item['data_pub']:
            if 'approved' == t['type']:
                list_item_approved = t['pub']
            elif 'refused' == t['type']:
                list_item_refused = t['pub']
            else:
                list_item_en_cour = t['pub']
        titre = u'بيانات تراخيص البناء'
        data = [{'title': u'الرخص بصدد الدرس', 'panel_type': 'panel-info', 'data_id': data_id, 'status': status + '/en_cours', 'list_item': list_item_en_cour}, 
                {'title': u'الرخص المقبولة', 'panel_type': 'panel-success', 'data_id': data_id, 'status': status + '/approved', 'list_item': list_item_approved}, 
                {'title': u'الرخص المرفوضة', 'panel_type': 'panel-danger', 'data_id': data_id, 'status': status + '/refused', 'list_item': list_item_refused}]
        if request.method == 'POST':
            keys = request.form.keys()
            keys.remove('data_id')
            for item in list_item['data_pub']:
                if item['type'] == types:
                    for p in item['pub']:
                        if p['db_name'] in keys:
                            p['status'] = True
                        else:
                            p['status'] = False
                    break
            dp = Data_Publisher.query.get(data_id)
            dp.data_pub = list_item['data_pub']
            dp.user_id = current_user.id
            db.session.commit()
            flash(u'لقد تم تحيين البيانات المنشورة لرخص البناء ', 'success')
            return redirect(url_for('permis_construction.consult_permisconst'))
    elif status == 'munproperty':
        list_item = Data_Publisher.query.filter_by(modules_id=4, municipal_id=current_user.municipal_id).first().__dict__
        data_id = list_item['id']
        for t in list_item['data_pub']:
            if 'public' == t['type']:
                list_item_public = t['pub']
            elif 'private' == t['type']:
                list_item_private = t['pub']
        titre = u'بيانات الملك البلدي'
        data = [{'title': u'الملك العام', 'panel_type': 'panel-info', 'data_id': data_id, 'status': status + '/public','list_item': list_item_public}, 
                {'title': u'الملك الخاص', 'panel_type': 'panel-info', 'data_id': data_id, 'status': status + '/private', 'list_item': list_item_private}]
        if request.method == 'POST':
            keys = request.form.keys()
            keys.remove('data_id')
            for item in list_item['data_pub']:
                if item['type'] == types:
                    for p in item['pub']:
                        if p['db_name'] in keys:
                            p['status'] = True
                        else:
                            p['status'] = False
                    break
            dp = Data_Publisher.query.get(data_id)
            dp.data_pub = list_item['data_pub']
            dp.user_id = current_user.id
            db.session.commit()
            flash(u'لقد تم تحيين البيانات المنشورة لملك البلدي ', 'success')
            return redirect(url_for('municipal_property.consult_municipal_property'))
    else:
        list_item = Data_Publisher.query.filter_by(modules_id=3, municipal_id=current_user.municipal_id).first().__dict__
        data_id = list_item['id']
        for t in list_item['data_pub']:
            if 'fourriere' == t['type']:
                list_item_fourriere = t['pub']
            elif 'detention' == t['type']:
                list_item_detention = t['pub']
        titre = u'بيانات مستودع الحجز'
        data = [{'title': u'المحجوز', 'panel_type': 'panel-info' ,'data_id': data_id, 'status': status + '/detention','list_item': list_item_detention}, 
                {'title': u'المستودعات', 'panel_type': 'panel-info','data_id': data_id, 'status': status + '/fourriere','list_item': list_item_fourriere}]
        if request.method == 'POST':
            keys = request.form.keys()
            keys.remove('data_id')
            for item in list_item['data_pub']:
                if item['type'] == types:
                    for p in item['pub']:
                        if p['db_name'] in keys:
                            p['status'] = True
                        else:
                            p['status'] = False
                    break
            dp = Data_Publisher.query.get(data_id)
            dp.data_pub = list_item['data_pub']
            dp.user_id = current_user.id
            db.session.commit()
            flash(u'لقد تم تحيين البيانات المنشورة لمستودع الحجز ', 'success')
            return redirect(url_for('fourrier.fourrier'))
    return render_template('admin/data_publisher.html', titre=titre, data=data)


def get_role(request, user_id):
    role_list = request.values.getlist('role')
    list_id = [_.id for _ in Users_Models.query.filter_by(user_id=user_id).all()]
    for m_id in list_id:
        db.session.delete(Users_Models.query.get(m_id))
    if role_list:
        for r in role_list:
            db.session.add(Users_Models(
                    user_id=user_id,
                    modules_id=int(r)))
            db.session.commit()    


def get_post(role):
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
    ckan = ckanapi.RemoteCKAN(app.config['CKAN_URL'], apikey=app.config['CKAN_API_KEY'])
    b = ckan.action.organization_create(**data)
    return b


def add_role_user(user):
    ckan = ckanapi.RemoteCKAN(app.config['CKAN_URL'], apikey=app.config['CKAN_API_KEY'])
    if user.ckan_id:
        municipality = Municipality.query.get(user.municipal_id)
        if municipality.ckan_id:
            dicti={'id': municipality.ckan_id, 'username': user.ckan_id, 'role': 'editor'}
            ckan.action.organization_member_create(**dicti)
            flash(u'تم إضافة %s %s إلى بلدية %s' %(user.name, user.last_name, municipality.municipal_name_ar), 'success')
            subject = u'تفعيل حساب  %s  %s' %(user.name, user.last_name) 
            template = render_template('admin/confirm_user_email.html', user=user)
            send_confirm_email([user.email], subject, template)
        else:
            flash(u'بلدية  هذا مستخدم ليس لديها معرف    CKAN', 'warning')
            subject = "Municipal don't have ckan_id"
            template = render_template('admin/alert_admin_email.html', user=user)
            send_admin_email(subject, template)
    else:
        flash(u'هذا مستخدم ليس لديه معرف  CKAN', 'warning')
        subject = "user does't have ckan_id"
        template = render_template('admin/alert_admin_email.html', user=user)
        send_admin_email(subject, template)

def get_ckan_organization_list():
    ckan = ckanapi.RemoteCKAN(app.config['CKAN_URL'], apikey=app.config['CKAN_API_KEY'])
    return ckan.action.organization_list()