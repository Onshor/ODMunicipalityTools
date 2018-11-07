# project/util.py
# -*- coding: utf-8 -*

from project import db
from project.models import Auto_update, Municipality, Users_Models
from flask_login import current_user
from project.ressource_api import update_ressource_api, update_ressource_api_request, package_exists
from flask import render_template, Blueprint, url_for, redirect, flash, request


def check_role(module_id):
    if Users_Models.query.filter_by(user_id=current_user.id, modules_id=module_id).first() or current_user.admin or current_user.municipal_admin:
        return True
    else:
        return False

def save_auto_update(file_name, category):
    auto_data = [d.file_name for d in Auto_update.query.filter_by(municipal_id=current_user.municipal_id).all()]
    if file_name not in auto_data:
        db_save_auto_update(file_name, category)
    return 0


def get_auto_update_data(f):
    id = Auto_update.query.filter_by(municipal_id=current_user.municipal_id, file_name=f['file_name']).first().id
    if Auto_update.query.filter_by(municipal_id=current_user.municipal_id, file_name=f['file_name']).first().ressource_id:
        check_r_id = True
    else:
        check_r_id = False
    return {'id': id, 'check_r_id': check_r_id, 'link': f['link'], 'api_key': current_user.api_key, 'type': f['type']}


def db_save_auto_update(file_name, category):
    auto_update = Auto_update(municipal_id=current_user.municipal_id,
                              file_name=file_name,
                              category=category)
    db.session.add(auto_update)
    db.session.commit()
    return 0


def push_api(r):
    if 'open_api' in r:
        api_data = get_api_data(r['r_id'], r['file_type'], r['link'])
        try:
            update_ressource_api(current_user.api_key, api_data)
            flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح','success')
        except:
            flash(u'الرجاء التثبت في api_key','warning')


def get_api_data(r_id, type, url):
    return {'r_id': Auto_update.query.filter_by(id=r_id).first().ressource_id,
            'type': type,
            'url': url,
            'name_mun_ar': Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar,
            'name_mun_fr': Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name}



