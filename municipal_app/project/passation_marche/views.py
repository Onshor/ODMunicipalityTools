# project/passation_marche/views.py
# -*- coding: utf-8 -*

#################
#### imports ####
#################

from pprint import pprint as pp
from project.decorators import check_confirmed
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_required, current_user
from parser import parse_passmarch

################
#### config ####
################

passmarch_blueprint = Blueprint('passation_marche', __name__,)
ALLOWED_EXTENSIONS = set(['xml', 'XML'])

################
#### routes ####
################


@passmarch_blueprint.route('/passmarch/adeb/<upload>', methods=['GET', 'POST'])
@passmarch_blueprint.route('/passmarch/adeb')
@login_required
@check_confirmed
def passmarch(upload=None):
    if upload:
        if request.method == 'POST':
            if 'file' not in request.files:
                flash(u'لا يوجد ملف', 'warning')
                return redirect(request.url)
            f = request.files['file']
            if f.filename == '':
                flash(u'لا يوجد ملف', 'warning')
                return redirect(request.url)
            if f and allowed_file(f.filename):
                pp(f.filename)
                pass_march_data = parse_passmarch(f)
                pp(pass_march_data)
                pp(len(pass_march_data))
            else:
                flash(u'صيغة ملف خاطئة ', 'warning')
    return render_template('passation_marche/passation_marche.html')





def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
