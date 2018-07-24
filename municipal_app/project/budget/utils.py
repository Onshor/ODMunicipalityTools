#!/usr/bin/env python
# -*- coding: utf-8 -*

from flask_login import current_user
from project.models import Budget_parametre, Budget_annuelle, Budget_mensuelle, Auto_update, File_log
from project import db
from parser import decode_unicode, get_csv_file, get_excel_file
from pprint import pprint as pp


ALLOWED_EXTENSIONS = set(['xml'])


def save_budget_parametre(budget_att):
    def update_budget_param(b):
        db.session.add(Budget_parametre(user_id=current_user.id,
                                        article=b['article'],
                                        paragraphe=b['paragraphe'],
                                        sous_paragraphe=b['sous_paragraphe'],
                                        titre=b['titre'],
                                        label=b['label'],
                                        type=b['type']))
        db.session.commit()
    param_list = list(set([_.titre + _.sous_paragraphe + _.paragraphe + _.article for _ in Budget_parametre.query.all()]))
    for b in budget_att:
        param_chech_id = b['titre'] + b['sous_paragraphe'] + b['paragraphe'] + b['article']
        if not Budget_parametre.query.all():
            update_budget_param(b)
        elif param_chech_id not in param_list:
            update_budget_param(b)
    return True


def save_budget_fee_annuelle(budget_att):
    def update_budget_annuel(b, param_id):
        db.session.add(Budget_annuelle(montant=b['montant'],
                                       insert_date=b['insert_date'],
                                       municipal_id=b['municipal_id'],
                                       reference=b['reference'],
                                       numero_maj=b['numero_maj'],
                                       parametre_id=param_id,
                                       year=b['year']))
        db.session.commit()
    log = False
    param_list = [{_.titre + _.sous_paragraphe + _.paragraphe + _.article: _.id} for _ in Budget_parametre.query.all()]
    ref_check = list(set([_.reference + _.numero_maj for _ in Budget_annuelle.query.all()]))
    for p in param_list:
        for k, v in p.iteritems():
            for b in budget_att:
                check_item = b['reference'] + b['numero_maj']
                if check_item not in ref_check:
                    param_chech_id = b['titre'] + b['sous_paragraphe'] + b['paragraphe'] + b['article']
                    if param_chech_id == k:
                        update_budget_annuel(b, v)
                        log = True
                else:
                    param_chech_id = b['titre'] + b['sous_paragraphe'] + b['paragraphe'] + b['article']
                    if param_chech_id == k:
                        if str(b['montant']) + b['municipal_id'] + b['reference'] + b['year'] + str(v) not in list(set([str(_.montant) + _.municipal_id + _.reference + _.year + str(_.parametre_id) for _ in Budget_annuelle.query.all()])):
                            update_budget_annuel(b, v)
                            log = True
    return log


def save_budget_fee_monthly(budget_att):
    def update_budget_param(b, param_id):
        db.session.add(Budget_mensuelle(montant=b['montant'],
                                        parametre_id=param_id,
                                        month=b['month'],
                                        year=int(b['year']),
                                        municipal_id=b['municipal_id']))
        db.session.commit()
    log = False
    param_list = [{_.titre + _.sous_paragraphe + _.paragraphe + _.article: _.id} for _ in Budget_parametre.query.all()]
    check_fee_monthly = list(set([str(_.montant) + str(_.month) + str(_.year) + str(_.municipal_id) for _ in Budget_mensuelle.query.all()]))
    for p in param_list:
        for k, v in p.iteritems():
            for b in budget_att:
                check_item = str(b['montant']) + str(b['month']) + str(b['year']) + b['municipal_id']
                param_chech_id = b['titre'] + b['sous_paragraphe'] + b['paragraphe'] + b['article']
                if param_chech_id == k and check_item not in check_fee_monthly:
                    update_budget_param(b, v)
                    log = True
    return log


def csv_annuelle_file():
    depecence_annuel, recette_annuel, years_list, p_id_list, budget_annuel_list = [], [], [], [], []
    depense_annuel_simple, recette_annuel_simple, budget_annuel_simple = [], [], []
    budget_annuel = Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id).all()
    for ba in budget_annuel:
        years_list.append(ba.year)
        p_id_list.append(ba.parametre_id)
    years_list = sorted(list(set(years_list)), key=int)
    for y in list(set(years_list)):
        for i in list(set(p_id_list)):
            b_year = Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id, year=y, parametre_id=i).order_by(Budget_annuelle.numero_maj.desc()).first()
            mont = b_year.montant if b_year else None
            budget_annuel_list.append({'p_id': i,
                                       y: mont})
            budget_annuel_simple.append({'p_id': i,
                                         'Year': y,
                                         'Budget': mont})
    for ba in budget_annuel_simple:
        budget_param = Budget_parametre.query.filter_by(id=ba['p_id']).first()
        p_dict_simple = get_dict_param(budget_param)
        if 'recette' in budget_param.type.lower():
            p_dict_simple.update({'Year': ba['Year'],
                                  'Budget': ba['Budget']})
            recette_annuel_simple.append(p_dict_simple)
        else:
            p_dict_simple.update({'Year': ba['Year'],
                                  'Budget': ba['Budget']})
            depense_annuel_simple.append(p_dict_simple)
    for i in list(set(p_id_list)):
        budget_param = Budget_parametre.query.filter_by(id=i).first()
        p_dict = get_dict_param(budget_param)
        if 'recette' in budget_param.type.lower():
            for a in budget_annuel_list:
                if a['p_id'] == i:
                    for v, k in a.iteritems():
                        if v != 'p_id':
                            p_dict.update({v: k})
            recette_annuel.append(p_dict)
        else:
            for a in budget_annuel_list:
                if a['p_id'] == i:
                    for v, k in a.iteritems():
                        if v != 'p_id':
                            p_dict.update({v: k})
            depecence_annuel.append(p_dict)
    recette_link_simple = get_csv_file(recette_annuel_simple, 'recette_simple_' + current_user.municipal_id, ['Year', 'Budget'])
    get_excel_file(recette_annuel_simple, 'recette_simple_' + current_user.municipal_id, ['Year', 'Budget'])
    save_auto_update(recette_link_simple)
    depecence_link_simple = get_csv_file(depense_annuel_simple, 'depense_simple_' + current_user.municipal_id, ['Year', 'Budget'])
    get_excel_file(depense_annuel_simple, 'depense_simple_' + current_user.municipal_id, ['Year', 'Budget'])
    save_auto_update(depecence_link_simple)
    recette_link_per_year = get_csv_file(recette_annuel, 'recette_per_year_' + current_user.municipal_id, years_list)
    get_excel_file(recette_annuel, 'recette_per_year_' + current_user.municipal_id, years_list)
    save_auto_update(recette_link_per_year)
    depecence_link_per_year = get_csv_file(depecence_annuel, 'depense_per_year_' + current_user.municipal_id, years_list)
    get_excel_file(depecence_annuel, 'depense_per_year_' + current_user.municipal_id, years_list)
    save_auto_update(depecence_link_per_year)
    return recette_link_simple, depecence_link_simple, recette_link_per_year, depecence_link_per_year


def get_dict_param(b):
    return {'Titre': b.titre,
            'Paragraphe': b.paragraphe,
            'Sous_paragraphe': b.sous_paragraphe,
            'Article': b.article,
            'Imputation': decode_unicode(b.label)}


def csv_mensuelle_file(b_type):
    p_id_month, final_list, order_list, check_list, approved_month_list = [], [], [], [], []
    budget_month = Budget_mensuelle.query.filter_by(municipal_id=current_user.municipal_id).all()
    month_list = [_.month for _ in budget_month]
    years_list = [_.year for _ in budget_month]
    p_id_list = [_.parametre_id for _ in budget_month]
    y = max(years_list)
    list_id_type = [_.id for _ in Budget_parametre.query.all() if _.type.lower() in b_type.lower()]
    while not check_list:
        for id_t in list_id_type:
            check_list.extend(Budget_mensuelle.query.filter_by(municipal_id=current_user.municipal_id, parametre_id=id_t, year=y).all())
        if check_list:
            pass
        else:
            y = y - 1
    for ml in list(set(month_list)):
        for id_t in list_id_type:
            if Budget_mensuelle.query.filter_by(municipal_id=current_user.municipal_id, parametre_id=id_t, year=y, month=ml).all():
                approved_month_list.append(ml)
    for i in list(set(p_id_list)):
        b_year = Budget_annuelle.query.filter_by(municipal_id=current_user.municipal_id, year=str(y), parametre_id=i).order_by(Budget_annuelle.numero_maj.desc()).first()
        if b_year:
            p_id_month_dict = {'Budget_' + str(y): b_year.montant,
                               'p_id': i}
            for m in list(set(approved_month_list)):
                if Budget_mensuelle.query.filter_by(municipal_id=current_user.municipal_id, year=y, month=m).first():
                    b_month = Budget_mensuelle.query.filter_by(municipal_id=current_user.municipal_id, year=y, parametre_id=i, month=m).first()
                    b_month_montant = b_month.montant if b_month else None
                    mm = str(m) if len(str(m)) == 2 else '0' + str(m)
                    p_id_month_dict['Budget_' + mm + '_' + str(y)] = b_month_montant
                    p_id_month.append(p_id_month_dict)
    for i in list(set(p_id_list)):
        budget_param = Budget_parametre.query.filter_by(id=i).first()
        if b_type.lower() in budget_param.type.lower():
            for a in p_id_month:
                if a['p_id'] == i:
                    p_dict = get_dict_param(budget_param)
                    for v, k in a.iteritems():
                        if v != 'p_id':
                            p_dict.update({v: k})
                    final_list.append(p_dict)
    for k, v in final_list[1].iteritems():
        if k.startswith('Budget'):
            order_list.append(k)
    order_list = sorted(order_list)
    # filename = b_type + '_' + 'mensuelle' + '_' + str(y) + '_' + current_user.municipal_id
    filename = b_type + '_' + 'mensuelle' + '_' + current_user.municipal_id
    unique = [dict(t) for t in set(tuple(sorted(d.items())) for d in final_list)]
    unique = sorted(unique, key=lambda k: k['Article'])
    link = get_csv_file(unique, filename, order_list)
    save_auto_update(link)
    return link, list(set(approved_month_list)), y


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_municipal_id(user_mun_id, file_mun_id):
    if user_mun_id == file_mun_id:
        return True
    else:
        return False


def check_monthly_data(d_type):
    check = False
    if Budget_mensuelle.query.filter_by(municipal_id=current_user.municipal_id).first():
        list_parameter = [_.id for _ in Budget_parametre.query.filter_by(type=d_type).all()]
        check_list = [_.parametre_id for _ in Budget_mensuelle.query.filter_by(municipal_id=current_user.municipal_id).all()]
        for i in list_parameter:
            if i in check_list:
                check = True
                break
    return check


def save_auto_update(file_name):
    auto_data = [d.file_name for d in Auto_update.query.filter_by(municipal_id=current_user.municipal_id).all()]
    if file_name not in auto_data:
        db_save_auto_update(file_name)
    return 0


def db_save_auto_update(file_name):
    auto_update = Auto_update(municipal_id=current_user.municipal_id,
                              file_name=file_name,
                              category='Budget')
    db.session.add(auto_update)
    db.session.commit()
    db_save_log_files(auto_update.id)
    return 0


def db_save_log_files(file_id):
    db.session.add(File_log(user_id=current_user.id,
                            municipal_id=current_user.municipal_id,
                            file_id=file_id))
    db.session.commit()
    return 0
