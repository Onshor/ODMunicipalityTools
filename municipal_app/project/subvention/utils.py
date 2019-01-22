#!/usr/bin/env python
# -*- coding: utf-8 -*

from flask_login import current_user
from project import db
from flask import flash, url_for
from pprint import pprint as pp
import csv
import os
import datetime
import xml.etree.ElementTree as et
from project.models import Budget_association, Auto_update, File_log


ALLOWED_EXTENSIONS = set(['xml'])


def decode_unicode(v):
    try:
        return v.encode('utf-8')
    except:
        return v


def reforme_date(date):
    month_list = {'01': 'jan',
                  '02': 'feb',
                  '03': 'mar',
                  '04': 'apr',
                  '05': 'may',
                  '06': 'jun',
                  '07': 'jul',
                  '08': 'aug',
                  '09': 'sep',
                  '10': 'oct',
                  '11': 'nov',
                  '12': 'dec'}
    dd = date.split('-')[0]
    mm = date.split('-')[1].lower()
    yy = date.split('-')[-1]
    for k, v in month_list.iteritems():
        if v == mm:
            mm = k
            break
    return dd + '/' + mm + '/20' + yy


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_xml(xml_file):
    data = []
    year = None
    parser = et.XMLParser(encoding="Windows-1256")
    tree = et.parse(xml_file, parser=parser)
    soup = tree.getroot()
    mun_id = None
    for item in soup.findall('LIST_G_ORD_NUMERO'):
        for item1 in item.findall('G_ORD_NUMERO'):
            year = item1.find('ORD_NUMERO').text[2:6]
            mun_id = item1.find('ORD_NUMERO').text[7:12]
            data.append({'Ordre_numero': item1.find('ORD_NUMERO').text,
                         'Benificiaire': decode_unicode(item1.find('ORD_NOMBEN').text),
                         'Date_orde': reforme_date(item1.find('ORD_DATEOR').text),
                         'Date_paiement': reforme_date(item1.find('ORD_DATECP').text),
                         'Montant_ordre': item1.find('LOR_BRTORD').text,
                         'Montant_paiement': item1.find('LOR_MNTPAY').text,
                         'Year': year})
    return data, mun_id


def get_csv_file(data, ref):
    fieldnames = ['Ord_numero', 'Benificiaire', 'Date_paiement', 'Montant_paiement', 'Annee']
    filepath = get_file_path() + ref + '.csv'
    with open(filepath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    return ref + '.csv'


def save_db(data):
    def save(d):
        db.session.add(Budget_association(municipal_id=current_user.municipal_id,
                                          user_id=current_user.id,
                                          year=d['Year'],
                                          ordre_numero=d['Ordre_numero'],
                                          benificiaire=d['Benificiaire'],
                                          date_orde=datetime.datetime.strptime(d['Date_orde'], "%d/%m/%Y"),
                                          date_paiement=datetime.datetime.strptime(d['Date_paiement'], '%d/%m/%Y'),
                                          montant_ordre=d['Montant_ordre'],
                                          montant_paiement=d['Montant_paiement']))
        db.session.commit()
    ordre_list = [_.ordre_numero for _ in Budget_association.query.filter_by(municipal_id=current_user.municipal_id).all()]
    exist = True
    for d in data:
        if d['Ordre_numero'] in ordre_list:
            pass
            exist = True
        else:
            save(d)
            exist = False
    flash(u'تم حفظها في قاعدة البيانات', 'success') if not exist else flash(u'لقد تم تحميل هذا الملف من قبل', 'info')
    return 0




def get_link_data():
    def get_data(data):
        new_data, year = [], []
        for d in data:
            new_data.append({'Ord_numero': d.ordre_numero,
                             'Benificiaire': decode_unicode(d.benificiaire),
                             'Date_paiement': d.date_paiement,
                             'Montant_paiement': d.montant_paiement,
                             'Annee': d.year})
            year.append(d.year)
        return new_data, ' ,'.join(sorted(list(set(year))))

    data = Budget_association.query.filter_by(municipal_id=current_user.municipal_id).all()
    if data:
        confirm_url = url_for('main.home', _external=True) + 'static/files/'
        data, year_str = get_data(data)
        link = get_csv_file(data, 'budget_association_' + current_user.municipal_id)
        save_auto_update(link)
        auto_list = [{'file_name': link, 'link': confirm_url + link, 'text': u'منح الجمعيات لسنوات ' + year_str, 'type': 'b_association'}]
        return get_auto_update_data(auto_list), year_str
    else:
        return None, None


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


def save_auto_update(file_name):
    auto_data = [d.file_name for d in Auto_update.query.filter_by(municipal_id=current_user.municipal_id).all()]
    if file_name not in auto_data:
        db_save_auto_update(file_name)
    return 0


def db_save_auto_update(file_name):
    auto_update = Auto_update(municipal_id=current_user.municipal_id,
                              file_name=file_name,
                              category='Budget_associtation')
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


def get_file_path():
    if os.path.isdir('project/static/files/'):
        return 'project/static/files/'
    else:
        return "/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/project/static/files/"
