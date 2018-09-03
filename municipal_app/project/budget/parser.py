#!/usr/bin/env python
# -*- coding: utf-8 -*

import xml.etree.ElementTree as et
import datetime
import csv
from list_month import decode_month
import os
from pprint import pprint as pp


def decode_unicode(v):
    try:
        return v.encode('utf-8')
    except:
        return v


def get_decode_month(mm): 
    month = ''
    for k, v in decode_month.iteritems():
        if mm.lower() in k:
            month = v
    return month


def get_g(g_child, maj=False):
    paragraphe = g_child.find('REC_PARAGR').text if g_child.find('REC_PARAGR') is not None else g_child.find('PAR_PARAGR').text
    sous_paragraphe = g_child.find('REC_SPARAG').text if g_child.find('REC_SPARAG') is not None else g_child.find('SPA_SPARAG').text
    label = g_child.find('LIBPAR').text if g_child.find('LIBPAR') is not None else g_child.find('LIBSPA').text
    montant = int(g_child.find('LRC_MNTAC1').text) if g_child.find('LRC_MNTAC1') is not None else int(g_child.find('LAR_MNTAC2').text)
    if maj:
        titre = None
    else:
        titre = g_child.find('REC_TITRES').text if g_child.find('REC_TITRES') is not None else g_child.find('TIT_TITRES').text
    budget_dict = {'paragraphe': paragraphe,
                   'sous_paragraphe': sous_paragraphe,
                   'titre': titre,
                   'label': label,
                   'montant': montant}
    return budget_dict


def parse_budget(xml_file):
    budget = []
    update = False
    parser = et.XMLParser(encoding="Windows-1256")
    tree = et.parse(xml_file, parser=parser)
    soup = tree.getroot()
    date = datetime.datetime.now()
    if soup.tag == 'AREPLFTMUN':
        municipal_id = soup.find('MUNICI').text
        reference = soup.find('REF').text
        year = soup.find('GESTION').text
        numero_maj = soup.find('NUM').text
        for item in soup:
            for g1_item in item.findall('G_1'):
                t = 'Recette'
                article = g1_item.find('REC_ARTICL').text
                for g1_child in g1_item.find('LIST_LIGNE').findall('LIGNE'):
                    budget_dict = get_g(g1_child)
                    budget_dict['type'] = t
                    budget_dict['article'] = article
                    budget_dict['reference'] = reference
                    budget_dict['year'] = year
                    budget_dict['municipal_id'] = municipal_id
                    budget_dict['numero_maj'] = numero_maj
                    budget_dict['insert_date'] = date
                    budget.append(budget_dict)
            for g2_item in item.findall('G_2'):
                t = 'Depence'
                article = g2_item.find('ART_ARTICL').text
                for g2_child in g2_item.find('LIST_G_LIGNEAUGMENTATION').findall('G_LIGNEAUGMENTATION'):
                    budget_dict = get_g(g2_child)
                    budget_dict['type'] = t
                    budget_dict['article'] = article
                    budget_dict['reference'] = reference
                    budget_dict['year'] = year
                    budget_dict['municipal_id'] = municipal_id
                    budget_dict['numero_maj'] = numero_maj
                    budget_dict['insert_date'] = date
                    budget.append(budget_dict)
    elif soup.tag == 'AREPMLFMUN':
        update = True
        municipal_id = soup.find('MUN').text
        reference = soup.find('REF').text
        year = soup.find('GESTION').text
        numero_maj = soup.find('NUM').text
        for item in soup:
            for item0 in item.findall('G_REC_TITRES'):
                titre = item0.find('REC_TITRES').text
                for g1_list in item0.findall('LIST_G_1'):
                    t = 'Recette'
                    for g1_item in g1_list.findall('G_1'):
                        article = g1_item.find('REC_ARTICL').text
                        for g1_child in g1_item.find('LIST_LIGNE').findall('LIGNE'):
                            budget_dict = get_g(g1_child, maj=True)
                            budget_dict['type'] = t
                            budget_dict['titre'] = titre
                            budget_dict['article'] = article
                            budget_dict['reference'] = reference
                            budget_dict['year'] = year
                            budget_dict['municipal_id'] = municipal_id
                            budget_dict['numero_maj'] = numero_maj
                            budget_dict['insert_date'] = date
                            budget.append(budget_dict)
            for item0 in item.findall('G_TIT_TITRES'):
                titre = item0.find('TIT_TITRES').text
                for g2_list in item0.findall('LIST_G_2'):
                    t = 'Depence'
                    for g2_item in g2_list.findall('G_2'):
                        article = g2_item.find('ART_ARTICL').text
                        for g2_child in g2_item.find('LIST_G_LIGNEAUGMENTATION').findall('G_LIGNEAUGMENTATION'):
                            budget_dict = get_g(g2_child, maj=True)
                            budget_dict['type'] = t
                            budget_dict['titre'] = titre
                            budget_dict['article'] = article
                            budget_dict['reference'] = reference
                            budget_dict['year'] = year
                            budget_dict['municipal_id'] = municipal_id
                            budget_dict['numero_maj'] = numero_maj
                            budget_dict['insert_date'] = date
                            budget.append(budget_dict)
    return budget, municipal_id, update


def parse_recette_file(xml_file):
    budget_mensuelle_recette = []
    parser = et.XMLParser(encoding="Windows-1256")
    tree = et.parse(xml_file, parser=parser)
    soup = tree.getroot()
    year = soup.find('CF_DATE').text.split('/')[0]
    month = soup.find('CF_DATE').text.split('/')[1].split('/')[-1]
    for list_g in soup.findall('LIST_G_1'):
        for g_mun in list_g.findall('G_1'):
            municipal_id = g_mun.find('MUN_MUNICI').text
            for g1 in g_mun.findall('LIST_G_REC_ARTICL'):
                for list_g_rec in g1.findall("G_REC_ARTICL"):
                    budget_mensuelle_recette.append({'type': 'Recette',
                                                     'month': int(month),
                                                     #  'montant': int(list_g_rec.find('FINAL').text),
                                                     'montant': int(list_g_rec.find('NET_REALISE').text),
                                                     'paragraphe': list_g_rec.find('REC_PARAGR').text,
                                                     'sous_paragraphe': list_g_rec.find('REC_SPARAG').text,
                                                     'article': list_g_rec.find('REC_ARTICL').text,
                                                     'titre': list_g_rec.find('REC_TITRES').text,
                                                     'municipal_id': municipal_id,
                                                     'label': list_g_rec.find('CF_LIB').text,
                                                     'year': year})
    return budget_mensuelle_recette, municipal_id


def parse_depence_file(xml_file):
    budget_mensuelle_depence = []
    parser = et.XMLParser(encoding="Windows-1256")
    tree = et.parse(xml_file, parser=parser)
    soup = tree.getroot()
    for list_g in soup.findall('LIST_G_1'):
        for g1 in list_g.findall('G_1'):
            month = get_decode_month(g1.find('CF_MOIS').text.replace(u'اضافي', '').replace(' ', ''))
            municipal_id = g1.find('MUN').text
            year = g1.find('GESTIO').text
            for list_titre in g1.findall('LIST_G_TIT'):
                for g_tit in list_titre.findall('G_TIT'):
                    titre = g_tit.find('TITRE').text
                    for list_g_prt in g_tit.findall("LIST_G_PRT"):
                        for g_prt in list_g_prt.findall('G_PRT'):
                            for list_g_art in g_prt.findall('LIST_G_ARTICLE'):
                                for g_art in list_g_art.findall('G_ARTICLE'):
                                    article = g_art.find('ARTICLE').text
                                    for list_g_chp in g_art.findall('LIST_G_CHP'):
                                        for g_chp in list_g_chp.findall('G_CHP'):
                                            budget_mensuelle_depence.append({'type': 'Depence',
                                                                             'titre': titre,
                                                                             'month': int(month),
                                                                             'montant': int(g_chp.find('CONPAY').text),
                                                                             'municipal_id': municipal_id,
                                                                             'article': article,
                                                                             'paragraphe': g_chp.find('PAR').text,
                                                                             'sous_paragraphe': g_chp.find('SPA').text,
                                                                             'label': g_chp.find('IMP').text,
                                                                             'year': int(year)})
    return budget_mensuelle_depence, municipal_id


def get_csv_file(data, ref, year_list):
    _ = ['Titre', 'Article', 'Paragraphe', 'Sous_paragraphe', 'Imputation']
    fieldnames = _ + year_list
    filepath = get_file_path() + ref + '.csv'
    with open(filepath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    return ref + '.csv'


def get_excel_file(data, ref, year_list):
    _ = ['Titre', 'Article', 'Paragraphe', 'Sous_paragraphe', 'Imputation']
    fieldnames = _ + year_list
    filepath = get_file_path() + ref + '.xls'
    with open(filepath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    return ref + '.xls'


def get_file_path():
    if os.path.isdir('project/static/files/'):
        return 'project/static/files/'
    else:
        return "/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/project/static/files/"
