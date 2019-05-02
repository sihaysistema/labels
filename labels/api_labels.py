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
def child_table_to_csv(dict_data, sticker_type):

    dict_data_csv = json.loads(dict_data)

    # frappe.msgprint(_(str(dict_data)))
    listado_items = []

    for item in dict_data_csv:
        cantidad = item['planned_qty']

        for i in range(cantidad):
            parseo_codigo = str(item['item_code'])

            nombre = frappe.get_value('Item', parseo_codigo, 'item_name')
            # frappe.msgprint(_(str(nombre)))

            # tupla_d = (item['item_name'], parseo_codigo[(len(parseo_codigo) - 13):])
            tupla_d = (nombre, parseo_codigo[(len(parseo_codigo) - 13):])
            listado_items.append(tupla_d)

    # frappe.msgprint(_(str(listado_items)))

    status_etiqueta = crear_etiqueta(listado_items, sticker_type)

    return status_etiqueta
