# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

import csv
import json
from datetime import datetime, date
from frappe.utils import get_site_name

# Permite trabajar con acentos, ñ, simbolos, etc
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

@frappe.whitelist()
def child_table_to_csv(dict_data):

    dict_data_csv = json.loads(dict_data)

    csv_file = 'salida.csv'
    csv_columns = []

    for column in dict_data_csv[0]:
        csv_columns.append(str(column))

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data_csv:
                writer.writerow(data)
    except IOError:
        frappe.msgprint(_('ERROR'))
    else:
        frappe.msgprint(_('OK'))

    # frappe.msgprint(_(str(data)))

    # [{"modified_by":"Administrator",
    # "name":"16f3fc204b",
    # "parent":"MFG-PP-2019-00001",
    # "creation":"2019-04-10 16:28:26.018175",
    # "modified":"2019-04-10 16:28:57.793399",
    # "item_code":"CAJA-CRAYONES-001",
    # "min_order_qty":0,
    # "idx":1,
    # "parenttype":"Production Plan","warehouse":"Todos los Almacenes - S",
    # "doctype":"Material Request Plan Item","owner":"Administrator","docstatus":1,"quantity":2,"requested_qty":0,"actual_qty":0,"parentfield":"mr_items"}]