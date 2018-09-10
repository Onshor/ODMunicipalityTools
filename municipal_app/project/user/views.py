#!/usr/bin/env python
# -*- coding: utf-8 -*

import datetime
from project.decorators import check_confirmed
from project.token import generate_confirmation_token, confirm_token
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from project.models import User, Municipality
from project.email import send_email
from project import db, bcrypt
from .forms import LoginForm, RegisterForm, ChangePasswordForm, ContactForm, ApiForm
from pprint import pprint as pp
import ckanapi


################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)
ALLOWED_EXTENSIONS = set(['xml'])

################
#### routes ####
################


@user_blueprint.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if form.validate_on_submit():
        d = {'name': form.name.data,
             'email': form.email.data,
             'tel': form.tel.data,
             'message': form.message.data,
             'municipalite': form.municipalite.data}
        email = "med@onshor.org"
        html = render_template('user/email.html', d=d)
        subject = u"Join demande from municipality  " + d['municipalite']
        send_email(email, subject, html)
        return render_template('user/contact.html', send=True)
    return render_template('user/contact.html', form=form)


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    choices = [{'value': None, 'name': u'المنطقة البلدية'}]
    choices.extend([{'value': _.municipal_id, 'name': _.municipal_name_ar + ' ' + _.municipal_name} for _ in Municipality.query.filter_by(approved=True).all() if _.municipal_id != '1'])
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        if form.municipal_id.data != 'None':
            name = (form.email.data.split('@')[0] + '_' + form.municipal_id.data).replace('.', '').replace('-', '')
            password = form.password.data
            fullname = form.name.data + ' ' + form.last_name.data
            email = form.email.data
            list_ckan_user = get_list_user()
            ckan_email_list = [_['email'] for _ in list_ckan_user]
            if email in ckan_email_list:
                for e in list_ckan_user:
                    if e['email'] == email:
                        api_dict = e
            else:
                api_dict = create_user_ckan(name, password, fullname, email)
            user = User(
                email=form.email.data,
                password=form.password.data,
                name=form.name.data,
                last_name=form.last_name.data,
                municipal_id=form.municipal_id.data,
                confirmed=False,
                deleted=False,
                activate=False,
                last_login=datetime.datetime.now(),
                phone_number=form.phone_number.data,
                work_position=form.work_position.data,
                api_key=api_dict['apikey'],
                ckan_id=api_dict['id']
            )
            db.session.add(user)
            db.session.commit()
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('user.confirm_email', token=token, _external=True)
            mun_name = Municipality.query.filter_by(municipal_id=str(form.municipal_id.data)).first().municipal_name
            html = render_template('user/activate.html', confirm_url=confirm_url, name=form.name.data, last_name=form.last_name.data, last_login=datetime.datetime.now(), mun_name=mun_name)
            subject = u"برجاء تأكيد بريدك الالكترونى"
            send_email(user.email, subject, html)
            login_user(user)
            flash(u'تم إرسال رسالة تأكيد عبر البريد الإلكتروني.', 'success')
            return redirect(url_for("user.unconfirmed"))
        else:
            flash(u'خانة المنطقة البلدية اجبارية', 'warning')
    return render_template('user/register.html', form=form, choices=choices)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        deleted_list = [_.email for _ in User.query.filter_by(deleted=True).all()]
        panned_list = deleted_list + [_.email for _ in User.query.filter_by(activate=False, confirmed=True).all()]
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            if form.email.data in panned_list:
                flash(u'لقد تم حظرك من المنظومة ,ارجاء الإتصال بمشرف التطبيقه', 'warning')
                return render_template('user/login.html', form=form)
            else:
                login_user(user)
                user.last_login = datetime.datetime.now()
                db.session.commit()
                flash(u'مرحباً', 'success')
                return redirect(url_for('main.home'))
        else:
            flash(u'البريد الإلكتروني  و  أو كلمة المرور  غير صالح', 'danger')
            return render_template('user/login.html', form=form)
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'لقد خرجت', 'success')
    return redirect(url_for('user.login'))


@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
@check_confirmed
def profile():
    apiform = ApiForm(request.form)
    form = ChangePasswordForm(request.form)
    mun = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email, last_name=current_user.last_name, name=current_user.name,
                                    municipal_id=current_user.municipal_id).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash(u'تم تحيين  كلمة السر', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Password change was unsuccessful.', 'danger')
            return redirect(url_for('user.profile'))
    if apiform.validate_on_submit():
        user = User.query.get(current_user.id)
        user.api_key = apiform.api_key.data
        db.session.commit()
        flash(u'تم اضافة / تحيين api key', 'success')
        return redirect(url_for('main.home'))
    return render_template('user/profile.html', form=form, mun=mun, apiform=apiform)


@user_blueprint.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash(u'تم تأكيد الحساب بالفعل. الرجاء تسجيل الدخول', 'success')
    else:
        user.confirmed = True
        user.activate = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash(u'لقد قمت بتأكيد حسابك. شكر!', 'success')
    return redirect(url_for('main.home'))


@user_blueprint.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('main.home')
    # flash(u'يرجى تأكيد حسابك!', 'warning')
    return render_template('user/unconfirmed.html')


@user_blueprint.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('user/activate.html', confirm_url=confirm_url)
    subject = u"تأكيد بريدك الالكترونى"
    send_email(current_user.email, subject, html)
    flash(u'تم إرسال رسالة تأكيد إلكترونية جديدة.', 'success')
    return redirect(url_for('user.unconfirmed'))


def create_user_ckan(name, password, fullname, email):
    ckan = ckanapi.RemoteCKAN('http://openbaladiati.tn/', apikey='545dd248-0887-47c5-ae65-248c2772a53b')
    user_dict = {'name': name, 'password': password, 'email': email, 'fullname': fullname}
    api_dict = ckan.action.user_create(**user_dict)
    return api_dict


def get_list_user():
    ckan = ckanapi.RemoteCKAN('http://openbaladiati.tn/', apikey='545dd248-0887-47c5-ae65-248c2772a53b')
    return ckan.action.user_list()
