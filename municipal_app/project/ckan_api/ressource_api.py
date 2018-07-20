#!/usr/bin/env python
# -*- coding: utf-8 -*


import ckanapi


def update_ressource_api(key, id, filename):
    ckan = ckanapi.RemoteCKAN('http://openbaladiati.tn/', apikey='key')
    resource_dict = {"id": id,
                     "description": "donneés barrages mises à jour",
                     "name_ar": u"données barrages(ar) maj ",
                     "description_ar": u"données barrages(ar)",
                     "name_fr": u"donneés barrages",
                     "name": u"DONNEES BARRAGES",
                     "file": filename,
                     "format": "csv"}
    api_dict = ckan.action.resource_update(**resource_dict)
    return api_dict