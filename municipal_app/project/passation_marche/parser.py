#!/usr/bin/env python
# -*- coding: utf-8 -*

import xml.etree.ElementTree as et
import datetime
import csv
import os
from pprint import pprint as pp


def decode_unicode(v):
    try:
        return v.encode('utf-8')
    except:
        return v


# def get_decode_month(mm):
#     month = ''
#     for k, v in decode_month.iteritems():
#         if mm.lower() in k:
#             month = v
#     return month


def parse_passmarch(xml_file):
    passmarch = []
    parser = et.XMLParser(encoding="Windows-1256")
    tree = et.parse(xml_file, parser=parser)
    soup = tree.getroot()
    for item in soup:
        if item.tag == 'LIST_G_1':
            for item0 in item.findall('G_1'):
                LIST_G_ANMAR = item0.find('LIST_G_ANMAR')
                AO_YEAR = item0.find('ANMAR').text
                for item1 in LIST_G_ANMAR.findall('G_ANMAR'):
                    AO_CODE = AO_YEAR + item1.find('NUMAR').text.strip().replace(' ', '')
                    AO_OBJET = item1.find('MAR_OBJETS').text.strip()
                    LIST_G_FSSR_OBJET = item1.find('LIST_G_FSSR_OBJET')
                    for item2 in LIST_G_FSSR_OBJET.findall('G_FSSR_OBJET'):
                        AO_NAT = item2.find('NAT').text
                        LIST_G_RUBMAR = item2.find('LIST_G_RUBMAR')
                        for item3 in LIST_G_RUBMAR.findall('G_RUBMAR'):
                            AO_RUBMAR = item3.find('RUBMAR').text
                            MONTANT_SIG = int(item3.find('MNTSIG').text)
                            MONTANT_ENG = int(item3.find('MNTENG').text)
                            MONTANT_ORD = int(item3.find('MNTORD').text)
                            MONTANT_PAY = int(item3.find('MNTPAY').text)
                            Imputation_budget = None
                            passmarch.append({'AO_YEAR': AO_YEAR,
                                              'AO_CODE': AO_CODE,
                                              'AO_OBJET': AO_OBJET,
                                              'AO_NAT': AO_NAT,
                                              'AO_RUBMAR': AO_RUBMAR,
                                              'MONTANT_SIG': MONTANT_SIG,
                                              'MONTANT_ENG': MONTANT_ENG,
                                              'MONTANT_ORD': MONTANT_ORD,
                                              'MONTANT_PAY': MONTANT_PAY,
                                              'Imputation_budget': Imputation_budget})
    return passmarch