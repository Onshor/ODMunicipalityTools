# project/budget/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from utils import *
from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from parser import parse_budget, parse_recette_file, parse_depence_file
from project.models import Budget_annuelle, Municipality, Auto_update
from list_month import decode_month_ar, decode_month_fr
from project.ressource_api import update_ressource_api, update_ressource_api_request, package_exists
from pprint import pprint as pp


################
#### config ####
################

budget_blueprint = Blueprint('budget', __name__,)


################
#### routes ####
################

@budget_blueprint.route('/budget')
@login_required
@check_confirmed
def budget():
    return render_template('budget/budget_annuel.html')


@budget_blueprint.route('/budget_annuel', methods=['GET', 'POST'])
@login_required
@check_confirmed
def budget_annuel():
    if Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id).first():
        confirm_url = url_for('main.home', _external=True) + 'static/files/'
        recette_link_simple, depecence_link_simple, recette_link_per_year, depecence_link_per_year = csv_annuelle_file()
        rcs = confirm_url + recette_link_simple
        dps = confirm_url + depecence_link_simple
        rcy = confirm_url + recette_link_per_year
        dpy = confirm_url + depecence_link_per_year
        years = Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id).all()
        years = [_.year for _ in years]
        year_str = ''
        for y in sorted(list(set(years))):
            year_str = year_str + ', ' + y if year_str else y
        auto_list = [{'file_name': recette_link_simple, 'link': rcs, 'text': u'الموارد تقديم أفقي لسنوات ' +  year_str, 'type': 'an_rec_h'},
                     {'file_name': recette_link_per_year, 'link': rcy, 'text': u'موارد تقديم عمودي لسنوات ' +  year_str, 'type': 'an_rec_v'},
                     {'file_name': depecence_link_simple, 'link': dps, 'text': u'النفقات تقديم أفقي لسنوات '+  year_str, 'type': 'an_dep_h'},
                     {'file_name': depecence_link_per_year, 'link': dpy, 'text': u'نفقات تقديم عمودي لسنوات ' +  year_str, 'type': 'an_dep_v'}]
        data = get_auto_update_data(auto_list)
        if 'open_api' in request.values:
            api_data = get_api_data(request.values['r_id'], request.values['file_type'], request.values['link'], str(max(years)), None, None)
            try:
                update_ressource_api(current_user.api_key, api_data)
                flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح','success')
            except:
                flash(u'الرجاء التثبت في api_key','warning')
        return render_template('budget/budget_annuel.html', data=data, parsed_annuel=True)
    return render_template('budget/budget_annuel.html', mun_name=Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar)


@budget_blueprint.route('/budget_depence_mensuelle', methods=['GET', 'POST'])
@login_required
@check_confirmed
def budget_depence_mensuelle():
    if Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id).first():
        if check_monthly_data("Depence"):
            confirm_url = url_for('main.home', _external=True) + 'static/files/'
            file_name, months, year = csv_mensuelle_file('Depence')
            month_list = decode_mm_ar(months)
            month_list_fr = decode_mm_fr(months)
            dpm = confirm_url + file_name
            data = [{'link': dpm, 'file_name': file_name, 'text': u'نفقات أشهر %s للسنة %s' % (month_list, str(year)), 'type': 'men_dep' }]
            data = get_auto_update_data(data)
            if 'open_api' in request.values:
                api_data = get_api_data(request.values['r_id'], request.values['file_type'], request.values['link'], str(year), month_list_fr, month_list)
                try:
                    update_ressource_api(current_user.api_key, api_data)
                    flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح','success')
                except:
                    flash(u'الرجاء التثبت في api_key','warning')
            return render_template('budget/budget_depence_mensuelle.html', dpm=dpm, parsed_dep=True, month_list=month_list, year=year , data=data)
    return render_template('budget/budget_depence_mensuelle.html', mun_name=Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar)


@budget_blueprint.route('/budget_recette_mensuelle', methods=['GET', 'POST'])
@login_required
@check_confirmed
def budget_recette_mensuelle():
    if Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id).first():
        if check_monthly_data("Recette"):
            confirm_url = url_for('main.home', _external=True) + 'static/files/'
            file_name, months, year = csv_mensuelle_file('Recette')
            month_list = decode_mm_ar(months)
            month_list_fr = decode_mm_fr(months)
            rcm = confirm_url + file_name
            data = [{'link': rcm, 'file_name': file_name, 'text': u'موارد أشهر %s للسنة %s' % (month_list, str(year)), 'type': 'men_rec' }]
            data = get_auto_update_data(data)
            if 'open_api' in request.values:
                api_data = get_api_data(request.values['r_id'], request.values['file_type'], request.values['link'], str(year), month_list_fr, month_list)
                try:
                    update_ressource_api(current_user.api_key, api_data)
                    flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح','success')
                except:
                    flash(u'الرجاء التثبت في api_key','warning')
            return render_template('budget/budget_recette_mensuelle.html', parsed_rect=True, data=data)
    return render_template('budget/budget_recette_mensuelle.html')


@budget_blueprint.route('/uploader', methods=['GET', 'POST'])
@login_required
@check_confirmed
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No selected file')
            return redirect(request.url)
        f = request.files['file']
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            confirm_url = url_for('main.home', _external=True) + 'static/files/'
            if request.values['file_type'] == 'annuel':
                # try:
                    b, file_mun_id, update = parse_budget(f)
                    check = check_municipal_id(current_user.municipal_id, file_mun_id)
                    if check:
                        save_budget_parametre(b)
                        log = save_budget_fee_annuelle(b)
                        flash(u'تم حفظها في قاعدة البيانات', 'success') if log else flash(u'لقد تم تحميل هذا الملف من قبل', 'info')
                        recette_link_simple, depecence_link_simple, recette_link_per_year, depecence_link_per_year = csv_annuelle_file()
                        rcs = confirm_url + recette_link_simple
                        dps = confirm_url + depecence_link_simple
                        rcy = confirm_url + recette_link_per_year
                        dpy = confirm_url + depecence_link_per_year
                        if log:
                            save_xml_file(f, 'b_annuel')
                            save_log([recette_link_simple, depecence_link_simple, recette_link_per_year, depecence_link_per_year])
                        years = Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id).all()
                        years = [_.year for _ in years]
                        year_str = ''
                        for y in sorted(list(set(years))):
                            year_str = year_str + ', ' + y if year_str else y
                        auto_list = [{'file_name': recette_link_simple, 'link': rcs, 'text': u'الموارد حسب السنة', 'type':'an_rec_h'},
                                     {'file_name': recette_link_per_year, 'link': rcy, 'text': u'موارد' + ' ' + year_str, 'type':'an_rec_v'},
                                     {'file_name': depecence_link_simple, 'link': dps, 'text': u'النفقات حسب السنة', 'type':'an_dep_h'},
                                     {'file_name': depecence_link_per_year, 'link': dpy, 'text': u'نفقات' + ' ' + year_str, 'type':'an_dep_v'}]
                        data = get_auto_update_data(auto_list)
                        if 'open_api' in request.values:
                            api_data = get_api_data(request.values['r_id'], request.values['file_type'], request.values['link'], str(max(years)), None, None)
                            try:
                                update_ressource_api(current_user.api_key, api_data)
                                flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح','success')
                            except:
                                flash(u'الرجاء التثبت في api_key','warning')
                        return render_template('budget/budget_annuel.html', data=data, parsed_annuel=True)
                    else:
                        flash(u'ملف من بلدية أخرى الرجاء التثبت', 'danger')
                        return redirect(url_for('budget.budget_annuel'))
                # except:
                    # flash(u'ملف خاطئ الرجاء التثبت من إسم الملف( AREPLFTMUN أو AREPMLFMUN)', 'danger')
                    # return redirect(url_for('budget.budget_annuel'))
            elif request.values['file_type'] == 'dep_month':
                try:
                    b, file_mun_id = parse_depence_file(f)
                    check = check_municipal_id(current_user.municipal_id, file_mun_id)
                    if check:
                        save_budget_parametre(b)
                        log = save_budget_fee_monthly(b)
                        flash(u'تم حفظها في قاعدة البيانات', 'success') if log else flash(u'لقد تم تحميل هذا الملف من قبل', 'info')
                        file_name, months, year = csv_mensuelle_file('Depence')                                                
                        month_list = decode_mm_ar(months)
                        month_list_fr = decode_mm_fr(months)
                        dpm = confirm_url + file_name
                        if log:
                            save_xml_file(f, 'b_depence_mensuelle')
                            save_log([file_name])
                        data = [{'link': dpm, 'file_name': file_name, 'text': u'نفقات أشهر %s للسنة %s' % (month_list, str(year)), 'type': 'men_dep' }]
                        data = get_auto_update_data(data)
                        if 'open_api' in request.values:
                            api_data = get_api_data(request.values['r_id'], request.values['file_type'], request.values['link'], str(year), month_list_fr, month_list)
                            try:
                                update_ressource_api(current_user.api_key, api_data)
                                flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح','success')
                            except:
                                flash(u'الرجاء التثبت في api_key','warning')
                        return render_template('budget/budget_depence_mensuelle.html', parsed_dep=True, data=data)
                    else:
                        flash(u'ملف من بلدية أخرى الرجاء التثبت', 'danger')
                        return redirect(url_for('budget.budget_depence_mensuelle'))
                except:
                    flash(u'ملف خاطئ الرجاء التثبت من إسم الملف( MREPSITMNS )', 'danger')
                    return redirect(url_for('budget.budget_depence_mensuelle'))
            else:
                try:
                    b, file_mun_id = parse_recette_file(f)
                    check = check_municipal_id(current_user.municipal_id, file_mun_id)
                    if check:
                        save_budget_parametre(b)
                        log = save_budget_fee_monthly(b)
                        flash(u'تم حفظها في قاعدة البيانات', 'success') if log else flash(u'لقد تم تحميل هذا الملف من قبل', 'info')
                        file_name, months, year = csv_mensuelle_file('Recette')
                        month_list = decode_mm_ar(months)
                        month_list_fr = decode_mm_fr(months)
                        rcm = confirm_url + file_name
                        if log:
                            save_xml_file(f, 'b_recette_mensuelle')
                            save_log([file_name])
                        data = [{'link': rcm, 'file_name': file_name, 'text': u'نفقات أشهر %s للسنة %s' % (month_list, str(year)), 'type': 'men_rec' }]
                        data = get_auto_update_data(data)
                        if 'open_api' in request.values:
                            api_data = get_api_data(request.values['r_id'], request.values['file_type'], request.values['link'], str(year), month_list_fr, month_list)
                            try:
                                update_ressource_api(current_user.api_key, api_data)
                                flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح','success')
                            except:
                                flash(u'الرجاء التثبت في api_key','warning')
                        return render_template('budget/budget_recette_mensuelle.html', parsed_rect=True, data=data)
                except:
                    flash(u'ملف خاطئ الرجاء التثبت من إسم الملف( MREPSUIREC )', 'danger')
                    return redirect(url_for('budget.budget_recette_mensuelle'))
    return render_template('budget/budget.html', parsed_annuel=False, parsed_rect=False, parsed_dep=False)


@budget_blueprint.route('/download_file', methods=['GET', 'POST'])
@login_required
@check_confirmed
def download_file():
    if request.method == 'GET':
        confirm_url = url_for('main.home', _external=True) + 'static/files/'
        recette_link_simple, depecence_link_simple, recette_link_per_year, depecence_link_per_year = csv_annuelle_file()
        rcs = confirm_url + recette_link_simple
        dps = confirm_url + depecence_link_simple
        rcy = confirm_url + recette_link_per_year
        dpy = confirm_url + depecence_link_per_year
        return render_template('budget/budget.html', rcs=rcs, dps=dps, rcy=rcy, dpy=dpy, parsed_annuel=True)
    return render_template('budget/budget.html', parsed_annuel=False, parsed_rect=False, parsed_dep=False)


def decode_mm_ar(months):
    list_month, month_str = [], []
    for m in months:
        for k, v in decode_month_ar.iteritems():
            if int(v) == m:
                list_month.append(k)
    for mm in list_month:
        month_str = month_str + ', ' + mm if month_str else mm
    return month_str


def decode_mm_fr(months):
    list_month, month_str = [], []
    for m in months:
        for k, v in decode_month_fr.iteritems():
            if int(v) == m:
                list_month.append(k)
    for mm in list_month:
        month_str = month_str + ', ' + mm if month_str else mm
    return month_str

def save_log(list_file):
    for f in list_file:
        file_id = Auto_update.query.filter_by(municipal_id=current_user.municipal_id, file_name=f).first().id
        db_save_log_files(file_id)
    return 0


def get_auto_update_data(list_files):
    list_data = []
    for f in list_files:
        id = Auto_update.query.filter_by(municipal_id=current_user.municipal_id, file_name=f['file_name']).first().id
        if Auto_update.query.filter_by(municipal_id=current_user.municipal_id, file_name=f['file_name']).first().ressource_id:
            check_r_id = True
        else:
            check_r_id = False
        list_data.append({'id': id, 'check_r_id': check_r_id, 'link': f['link'], 'text': f['text'], 'api_key': current_user.api_key, 'type': f['type']})
    return list_data


def get_api_data(r_id, type, url, y, m_fr, m_ar):
    return {'r_id': Auto_update.query.filter_by(id=r_id).first().ressource_id,
            'type': type,
            'url': url,
            'name_mun_ar': Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name_ar,
            'name_mun_fr': Municipality.query.filter_by(municipal_id=current_user.municipal_id).first().municipal_name,
            'last_year': y,
            'last_month': m_fr,
            'last_month_ar': m_ar}