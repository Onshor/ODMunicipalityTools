# project/decorators.py
# -*- coding: utf-8 -*
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash(u'يرجى تأكيد حسابك!', 'warning')
            return redirect(url_for('user.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function


def check_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.admin is False:
            flash(u' ليس لديك إمكانية الولوج لهذه الصفحة', 'danger')
            return redirect(url_for('main.home'))
        return func(*args, **kwargs)

    return decorated_function
