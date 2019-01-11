#!/usr/bin/env python
# -*- coding: utf-8 -*


import ckanapi
from project import app
from flask import flash
from os.path import exists
import unidecode
from project import db
from project.models import Municipality, Packages, Resources
import xml.etree.ElementTree as et
from flask_login import current_user


def save_pack_resource_db(dataset_list, module_id, package_type):
    db.session.add(Packages(municipal_id=current_user.municipal_id,
                            modules_id=module_id,
                            package_id=dataset_list['id'],
                            package_type=package_type))
    db.session.commit()
    for r in dataset_list['resources']:
        db.session.add(Resources(municipal_id=current_user.municipal_id,
                                 resource_id=r['id'],
                                 package_id=dataset_list['id'],
                                 link=r['url']))
        db.session.commit()
    return 0


def insert_data(data, links_data):
    for d in data['resources']:
        for l in links_data:
            if l['type'] == d['type']:
                d['url'] = l['link']
    for d in data['resources']:
        del(d['type'])
    return data


def get_resource_dict(data, package_type, module_id):
    pack_id = Packages.query.filter_by(modules_id=str(module_id), package_type=package_type, municipal_id=current_user.municipal_id).first().package_id
    resources_ids = [{'url': _.link, 'r_id': _.resource_id} for _ in Resources.query.filter_by(package_id=pack_id).all()]
    for d in data:
        for r in resources_ids:
            if d['url'] == r['url']:
                d['id'] = r['r_id']
    return data


def get_file_path():
    if exists('project/metadata.xml'):
        return 'project/metadata.xml'
    else:
        return "/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/project/metadata.xml"


def read_metadata(xml_file, module_id, package_type, year_str, month_str, month_str_ar):
    metadata = {}
    mun_name = Municipality.query.filter_by(municipal_id=current_user.municipal_id).first()
    tree = et.parse(xml_file)
    soup = tree.getroot()
    for item in soup.findall('module'):
        if int(item.get('id')) == module_id:
            for pack in item.find('packages').findall('package'):
                if package_type == pack.get('id'):
                    metadata = {"name": pack.find('name').text.replace('mun_name', unidecode.unidecode(mun_name.municipal_name)).lower().replace(' ', '-'),
                                "title": pack.find('title').text.replace('mun_name', mun_name.municipal_name),
                                "title_ar": pack.find('title_ar').text.replace('mun_name_ar', mun_name.municipal_name_ar),
                                "notes": pack.find('notes').text.replace('mun_name', mun_name.municipal_name),
                                "notes_ar": pack.find('notes_ar').text.replace('mun_name_ar', mun_name.municipal_name_ar),
                                "frequency_update": pack.find('frequency_update').text,
                                "keywords": {"ar": [_.replace('mun_name_ar', '') for _ in pack.find('keywords_ar').text.split(',')],
                                             "fr": [_.replace('mun_name', mun_name.municipal_name) for _ in pack.find('keywords_fr').text.split(',')]},
                                "author": current_user.name + ' ' + current_user.last_name,
                                "author_email": current_user.email,
                                "maintainer": current_user.name + ' ' + current_user.last_name,
                                "maintainer_email": current_user.email,
                                "owner_org": mun_name.ckan_id,
                                "private": False,
                                "license_id": 'cc-by',
                                "groups": [{'name': pack.find('groups').text}],
                                "resources": []
                                }
                    for res in pack.find('resources').findall('resource'):
                        metadata['resources'].append({'description': res.find('description').text.replace('mun_name', mun_name.municipal_name).replace('YYYY', year_str).replace('MMMM', month_str),
                                                      'description_ar': res.find('description_ar').text.replace('mun_name_ar', mun_name.municipal_name_ar).replace('YYYY', year_str).replace('MMMM_ar', month_str_ar),
                                                      'name': res.find('name').text.replace('mun_name', mun_name.municipal_name).replace('YYYY', year_str).replace('MMMM', month_str),
                                                      'name_ar': res.find('name_ar').text.replace('mun_name_ar', mun_name.municipal_name_ar).replace('YYYY', year_str).replace('MMMM_ar', month_str_ar),
                                                      'format': res.find('format').text,
                                                      'type': res.get('id')})
                    break
            break
    return metadata


def create_dataset(module_id, package_type, links_data, year_str, month_str, month_str_ar):
    resource_list = []
    data = read_metadata(get_file_path(), module_id, package_type, year_str, month_str, month_str_ar)
    ckan = ckanapi.RemoteCKAN(app.config['CKAN_URL'], apikey=app.config['CKAN_API_KEY'])
    if data['name'] in ckan.action.package_list():
        data['name'] = data['name'] + '-001'
    data = insert_data(data, links_data)
    dataset_list = ckan.action.package_create(**data)
    for r in dataset_list['resources']:
        resource_list.append(r['id'])
    save_pack_resource_db(dataset_list, module_id, package_type)
    return dataset_list


def update_resource(module_id, package_type, links_data, year_str, month_str, month_str_ar):
    ckan = ckanapi.RemoteCKAN('http://openbaladiati.tn/', apikey=current_user.api_key)
    data = read_metadata(get_file_path(), module_id, package_type, year_str, month_str, month_str_ar)
    data = insert_data(data, links_data)
    resources_list = get_resource_dict(data['resources'], package_type, module_id)
    for resource_dict in resources_list:
        ckan.action.resource_update(**resource_dict)
    return 0


def module_publisher(module_id, package_type, links_data, year_str, month_str, month_str_ar):
    if Packages.query.filter_by(modules_id=str(module_id), package_type=package_type, municipal_id=current_user.municipal_id).first():
        update_resource(module_id, package_type, links_data, year_str, month_str, month_str_ar)
        flash(u'تم تحديث منظومة البيانات المفتوحة فالمنصة بنجاح', 'success')
    else:
        create_dataset(module_id, package_type, links_data, year_str, month_str, month_str_ar)
        flash(u'تم نشر منظومة البيانات المفتوحة فالمنصة بنجاح', 'success')
    return 0