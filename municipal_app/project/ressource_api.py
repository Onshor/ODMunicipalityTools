#!/usr/bin/env python
# -*- coding: utf-8 -*


import ckanapi
import requests
import json


def update_ressource_api(key, data):
    ckan = ckanapi.RemoteCKAN('http://openbaladiati.tn/', apikey=key)
    resource_dict = get_resource_dict(data)
    api_dict = ckan.action.resource_update(**resource_dict)
    return api_dict


def package_exists(pkg_name, key):
    r_id_list = []
    headers = {"content-type": "application/json", "Authorization": key}
    r = requests.get("http://openbaladiati.tn/api/action/resource_search?query=url:%s" % pkg_name, headers=headers)
    jdata = json.loads(r.text)
    for d in jdata['result']['results']:
      r_id_list.append(d['id'])
    return r_id_list


def get_resource_dict(data):
  resource_dict = {"id": data['r_id'],
                   "url": data['url'],
                   "format": "csv"}
  if data['type'] == 'an_rec_v':
    resource_dict.update({"description": u"Suivi annuel du budget des recettes de la Municipalité " + data['name_mun_fr'] + u" une présentation verticale qui consiste à regrouper les budgets annuel des recettes dans une seule colonne (les montants les uns en dessous des autres selon les années).",
                          "name_ar": u"الميزانيّة السنويّة للموارد حسب تقديم عمودي منذ سنة " + data['last_year'],
                          "description_ar": u"المتابعة السنويّة لميزانيّة الموارد ببلديّة " + data['name_mun_ar'] + u" حسب تقديم عمودي يعتمد على تجميع ميزانيّات الموارد عموديّا  (الميزانيّة السنويّة الواحدة تحت الأخرى حسب السنوات).",
                          "name_fr": u"Budget annuel des recettes selon une présentation verticale depuis " + data['last_year'],
                          "name": u"Budget annuel des recettes selon une présentation verticale depuis " + data['last_year']})
  elif data['type'] == 'an_dep_h':
    resource_dict.update({"description": u"Suivi annuel du budget des dépenses de la Municipalité de " + data['name_mun_fr'] + u" selon une présentation horizontale qui consiste à aligner le budget annuel des dépenses (les montants les uns à la suite des autres selon les années) sur toute la longueur du fichier contenant les données.",
                          "name_ar": u"الميزانيّة السنويّة للنفقات حسب تقديم أفقي منذ سنة " + data['last_year'],
                          "description_ar": u"المتابعة السنويّة لميزانيّة النفقات ببلديّة " + data['name_mun_ar'] + u" حسب تقديم أفقي يعتمد على تصفيف ميزانيّات النفقات أفقيّا (الميزانيّة السنويّة الواحدة إلى  جانب الأخرى) على امتداد كامل الملّف الذي يحتوي على البيانات.",
                          "name_fr": u"Budget annuel des dépenses selon une présentation horizontale depuis " + data['last_year'],
                          "name": u"Budget annuel des dépenses selon une présentation horizontale depuis " + data['last_year']})
  elif data['type'] == 'an_rec_h':
    resource_dict.update({"description": u"Suivi annuel du budget des recettes de la Municipalité de " + data['name_mun_fr'] + u" selon une présentation horizontale qui consiste à aligner le budget annuel des recettes (les montants les uns à la suite des autres selon les années) sur toute la longueur du fichier contenant les données.",
                          "name_ar": u"الميزانيّة السنويّة للموارد حسب تقديم أفقي منذ سنة" + data['last_year'],
                          "description_ar": u"لمتابعة السنويّة لميزانيّة الموارد ببلديّة " + data['name_mun_ar'] + u" حسب تقديم أفقي يعتمد على تصفيف ميزانيّات الموارد أفقيّا (الميزانيّة السنويّة الواحدة إلى جانب الأخرى) على امتداد كامل الملّف الذي يحتوي على البيانات.",
                          "name_fr": u"Budget annuel des recettes selon une présentation horizontale " + data['last_year'],
                          "name": u"Budget annuel des recettes selon une présentation horizontale " + data['last_year']})
  elif data['type'] == 'an_dep_v':
    resource_dict.update({"description": u"Suivi annuel du budget des dépenses de la Municipalité de  " + data['name_mun_fr'] + u" selon une présentation verticale qui consiste à regrouper les budgets annuel des dépenses dans une seule colonne (les montants les uns en dessous des autres selon les années).",
                          "name_ar": u"الميزانيّة السنويّة للنفقات حسب تقديم عمودي منذ سنة " + data['last_year'],
                          "description_ar": u" المتابعة السنويّة لميزانيّة النفقات ببلديّة " + data['name_mun_ar'] + u" حسب تقديم عمودي يعتمد على تجميع ميزانيّات النفقات عموديّا  (الميزانيّة السنويّة الواحدة تحت الأخرى حسب السنوات).",
                          "name_fr": u"Budget annuel des dépenses selon une présentation verticale depuis " + data['last_year'],
                          "name": u"Budget annuel des dépenses selon une présentation verticale depuis " + data['last_year']})
  elif data['type'] == 'men_dep':
    resource_dict.update({"description": u"Evolution mensuelle des dépenses à la municipalité de " + data['name_mun_fr'] + u" jusqu’au " + data['last_month'] + ' ' + data['last_year'],
                          "name_ar": u"النفقات الشهرية لى " + data['last_month_ar'] + ' ' + data['last_year'],
                          "description_ar": u"تطوّر النفقات الشهريّة لى " + data['last_month_ar'] + ' ' + data['last_year'] + u" ببلديّة " + data['name_mun_ar'],
                          "name_fr": u"Dépenses mensuelles jusqu’au " + data['last_month'] + ' ' + data['last_year'],
                          "name": u"Dépenses mensuelles jusqu’au " + data['last_month'] + ' ' + data['last_year']})
  elif data['type'] == 'men_rec':
    resource_dict.update({"description": u"Evolution mensuelle des ressources à la municipalité de  " + data['name_mun_fr'] + u" jusqu’au " + data['last_month'] + ' ' + data['last_year'],
                          "name_ar": u"الموارد الشهرية لى  " + data['last_month_ar'] + ' ' + data['last_year'],
                          "description_ar": u"تطوّر الموارد الشهريّة لى " + data['last_month_ar'] + ' ' + data['last_year'] + u" ببلديّة " + data['name_mun_ar'],
                          "name_fr": u"Recettes mensuelles jusqu’au " + data['last_month'] + ' ' + data['last_year'],
                          "name": u"Recettes mensuelles jusqu’au " + data['last_month'] + ' ' + data['last_year']})
  elif data['type'] == 'pc_approved':
    resource_dict.update({"description": u'Les permis de construire approuvés par la municipalité de %s' % data['name_mun_fr'],
                          "name_ar": u'رخص البناء المصادق عليه',
                          "description_ar": u'قائمة رخص البناء المصادق عليها من قبل بلدية %s' % data['name_mun_ar'],
                          "name_fr": u"Permis de construire approuvés",
                          "name": u"Permis de construire approuvés"})
  elif data['type'] == 'pc_en_cours':
    resource_dict.update({"description": u'Liste permissions de construction en cours de traitement à la municipalité de %s' % data['name_mun_fr'],
                          "name_ar": u'رخص البناء بصدد الدرس',
                          "description_ar": u'قائمة رخص البناء بصدد الدرس ببلدية %s' % data['name_mun_ar'],
                          "name_fr": u"Permis de construire en cours de traitement",
                          "name": u"Permis de construire en cours de traitement"})
  elif data['type'] == 'pc_refused':
    resource_dict.update({"description": u"Liste des demandes d'autorisations de bâtir refusées à la municipalité de  %s" % data['name_mun_fr'],
                          "name_ar": u'رخص البناء المرفوضة',
                          "description_ar": u'قائمة رخص البناء المرفوضة ببلدية %s' % data['name_mun_ar'],
                          "name_fr": u"Permis de construire refusés",
                          "name": u"Permis de construire refusés"})
  elif data['type'] == 'mp_private':
    resource_dict.update({"description": u'Liste des propriétés municipales privées à la municipalité de %s' % data['name_mun_fr'],
                          "name_ar": u'الملك البلدي الخاص',
                          "description_ar": u'القائمة كاملة للملك البلدي الخاص ببلديّة %s' % data['name_mun_ar'],
                          "name_fr": u"Propriétés municipales privées",
                          "name": u"Propriétés municipales privées"})
  elif data['type'] == 'mp_public':
    resource_dict.update({"description": u'Liste complète des propriétés municipales publiques à la municipalité de %s' % data['name_mun_fr'],
                          "name_ar": u'الملك البلدي العام',
                          "description_ar": u'القائمة كاملة للملك البلدي العام ببلديّة %s' % data['name_mun_ar'],
                          "name_fr": u"Propriétés municipales publiques",
                          "name": u"Propriétés municipales publiques"})
  elif data['type'] == 'fourriere':
    resource_dict.update({"description": u'Liste complète des fourrières municipales avec les coordonnées géographiques.',
                          "name_ar": u'قائمة مستودعات الحجز البلد',
                          "description_ar": u'قائمة مستودعات الحجز البلدي ببلديّة بوعرادة مع تحديد موقعها الجغرافي.',
                          "name_fr": u"Liste des fourrières municipales",
                          "name": u"Liste des fourrières municipales"})
  elif data['type'] == 'detention':
    resource_dict.update({"description": u'Liste des objets détenus dans la fourrière municipale de la commune de %s' % data['name_mun_fr'],
                          "name_ar": u'سجّل الحجز البلدي',
                          "description_ar": u'قائمة المحجوزات بمستودعات الحجز البلدي ببلديّة %s' % data['name_mun_ar'],
                          "name_fr": u"Registre de mise en fourrière",
                          "name": u"Registre de mise en fourrière"})
  return resource_dict


def update_ressource_api_request():
    r = requests.post('http://openbaladiati.tn/api/action/resource_update',
                      data=json.loads(json.dumps({"id": "b66be040-c00b-404b-9eab-9119cbbf2122",
                           "description": " barrages mises à jour",
                           "name_ar": " barrages(ar) maj ",
                           "description_ar": " barrages(ar) sdgsd",
                     "name_fr": " barrages",
                     "name": "DONNEES BARRAGES",
                     "format": "csv"})),
                      headers={"X-CKAN-API-Key": "545dd248-0887-47c5-ae65-248c2772a53b"},)
    return r.text