# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

import csv
import json
from datetime import datetime, date
from frappe.utils import get_site_name

from resources.pdf_sticker_generator import crear_etiqueta

# Permite trabajar con acentos, ñ, simbolos, etc
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

@frappe.whitelist()
def child_table_to_csv(dict_data):

    dict_data_csv = json.loads(dict_data)

    # frappe.msgprint(_(str(dict_data)))
    listado_items = []

    for item in dict_data_csv:
        cantidad = item['quantity']

        for i in range(cantidad):
            parseo_codigo = str(item['item_code'])
            tupla_d = (item['item_name'], parseo_codigo[(len(parseo_codigo) - 13):])
            listado_items.append(tupla_d)

    frappe.msgprint(_(str(listado_items)))

    crear_etiqueta(listado_items)
    # csv_file = 'salida.csv'
    # csv_columns = ['item_code', 'item_name', 'quantity']

    # # for column in dict_data_csv[0]:
    # #     csv_columns.append(str(column))

    # try:
    #     with open(csv_file, 'w') as csvfile:
    #         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    #         writer.writeheader()

    #         for data in dict_data_csv:
    #             del data['modified_by']
    #             del data['parent']
    #             del data['creation']
    #             del data['modified']
    #             del data['min_order_qty']
    #             del data['idx']
    #             del data['parenttype']
    #             del data['warehouse']
    #             del data['doctype']
    #             del data['owner']
    #             del data['docstatus']
    #             del data['requested_qty']
    #             del data['actual_qty']
    #             del data['parentfield']
    #             del data['name']
    #             writer.writerow(data)

    # except IOError:
    #     frappe.msgprint(_('ERROR'))
    # else:
    #     # crear_etiqueta()
    #     frappe.msgprint(_(str(len(dict_data_csv))))