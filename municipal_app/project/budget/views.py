# project/budget/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from utils import save_budget_fee_annuelle, save_budget_fee_monthly, csv_annuelle_file, allowed_file, check_municipal_id, save_budget_parametre, csv_mensuelle_file
from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from parser import parse_budget, parse_recette_file, parse_depence_file


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
    return render_template('budget/budget.html')


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
                try:
                    b, file_mun_id, update = parse_budget(f)
                    check = check_municipal_id(current_user.municipal_id, file_mun_id)
                    if check:
                        save_budget_parametre(b)
                        save_budget_fee_annuelle(b)
                        flash(u'تم حفظها في قاعدة البيانات', 'success')
                        recette_link_simple, depecence_link_simple, recette_link_per_year, depecence_link_per_year = csv_annuelle_file()
                        rcs = confirm_url + recette_link_simple
                        dps = confirm_url + depecence_link_simple
                        rcy = confirm_url + recette_link_per_year
                        dpy = confirm_url + depecence_link_per_year
                        return render_template('budget/budget.html', rcs=rcs, dps=dps, rcy=rcy, dpy=dpy, parsed_annuel=True)
                    else:
                        flash(u'ملف من بلدية أخرى الرجاء التثبت', 'danger')
                        return redirect(request.url)
                except:
                    flash(u'ملف خاطئ الرجاء التثبت من إسم الملف( AREPLFTMUN أو AREPMLFMUN)', 'danger')
                    return redirect(request.url)
            elif request.values['file_type'] == 'dep_month':
                try:
                    b, file_mun_id = parse_depence_file(f)
                    check = check_municipal_id(current_user.municipal_id, file_mun_id)
                    if check:
                        save_budget_parametre(b)
                        save_budget_fee_monthly(b)
                        dpm = csv_mensuelle_file('Depence')
                        dpm = confirm_url + dpm
                        flash(u'تم حفظها في قاعدة البيانات', 'success')
                        return render_template('budget/budget.html', dpm=dpm, parsed_dep=True)
                    else:
                        flash(u'ملف من بلدية أخرى الرجاء التثبت', 'danger')
                        return redirect(request.url)
                except:
                    flash(u'ملف خاطئ الرجاء التثبت من إسم الملف( MREPSITMNS )', 'danger')
                    return redirect(request.url)
            else:
                try:
                    b, file_mun_id = parse_recette_file(f)
                    check = check_municipal_id(current_user.municipal_id, file_mun_id)
                    if check:
                        save_budget_parametre(b)
                        save_budget_fee_monthly(b)
                        rcm = csv_mensuelle_file('Recette')
                        rcm = confirm_url + rcm
                        flash(u'تم حفظها في قاعدة البيانات', 'success')
                        return render_template('budget/budget.html', rcm=rcm, parsed_rect=True)
                    else:
                        flash(u'ملف من بلدية أخرى الرجاء التثبت', 'danger')
                        return redirect(request.url)
                except:
                    flash(u'ملف خاطئ الرجاء التثبت من إسم الملف( MREPSUIREC )', 'danger')
                    return redirect(request.url)
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
