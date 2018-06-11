# project/admin/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from project.models import User, Municipality
from .forms import ChangePwdForm
from pprint import pprint as pp
from project import db, bcrypt


################
#### config ####
################


admin_blueprint = Blueprint('admin', __name__,)


@admin_blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
@check_confirmed
def admin():
    if current_user.admin:
        if 'dasactivation' in request.values:
            user_id = request.values['id']
            user = User.query.get(int(user_id))
            user.confirmed = False
            db.session.commit()
            return redirect(url_for('admin.admin'))
        elif 'activer' in request.values:
            user_id = request.values['id']
            user = User.query.get(int(user_id))
            user.confirmed = True
            db.session.commit()
            return redirect(url_for('admin.admin'))
        new_list = []
        list_user = [u.__dict__ for u in User.query.all()]
        for u in list_user:
            if not u['admin']:
                new_list.append({'confirmed': u['confirmed'],
                                 'confirmed_on': u['confirmed_on'].strftime("%d/%m/%Y") if u['confirmed'] and u['confirmed_on'] else None,
                                 'name': u['name'],
                                 'id': u['id'],
                                 'email': u['email'],
                                 'last_name': u['last_name'],
                                 'municipality': Municipality.query.filter_by(municipal_id=u['municipal_id']).first().municipal_name if int(u['municipal_id']) != 1 else 'Super Admin',
                                 'register_on': u['registered_on'].strftime("%d/%m/%Y")})
        return render_template('admin/admin.html', list_user=new_list)
    else:
        flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'warning')
        return redirect(url_for('main.home'))


@admin_blueprint.route('/admin/editpwd/<id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_pawd_admin(id):
    form = ChangePwdForm()
    user = User.query.filter_by(id=int(id)).first().__dict__
    mun = Municipality.query.filter_by(municipal_id=str(user['municipal_id'])).first()
    mun = mun.municipal_name
    if form.validate_on_submit():
        user_admin = User.query.filter_by(email=current_user.email).first()
        if user_admin and bcrypt.check_password_hash(user_admin.password, request.form['admin_password']):
            user = User.query.filter_by(id=int(id)).first()
            if user:
                user.password = bcrypt.generate_password_hash(form.password.data)
                db.session.commit()
                flash('Password successfully changed.', 'success')
                return redirect(url_for('admin.admin'))
            else:
                flash('Password change was unsuccessful.', 'danger')
                return render_template('admin/edit_pwd_admin.html', form=form, user=user, mun=mun)
        else:
            flash(u'vérifier votre mot de passe', 'danger')
            return render_template('admin/edit_pwd_admin.html', form=form, user=user, mun=mun)
    return render_template('admin/edit_pwd_admin.html', form=form, user=user, mun=mun)