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

    # frappe.msgprint(_(str(dict_data)))

    csv_file = 'salida.csv'
    csv_columns = ['item_code', 'item_name', 'quantity']

    # for column in dict_data_csv[0]:
    #     csv_columns.append(str(column))

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()

            for data in dict_data_csv:
                del data['modified_by']
                del data['parent']
                del data['creation']
                del data['modified']
                del data['min_order_qty']
                del data['idx']
                del data['parenttype']
                del data['warehouse']
                del data['doctype']
                del data['owner']
                del data['docstatus']
                del data['requested_qty']
                del data['actual_qty']
                del data['parentfield']
                del data['name']
                writer.writerow(data)

    except IOError:
        frappe.msgprint(_('ERROR'))
    else:
        frappe.msgprint(_('OK'))

    ## required columns
    # Item Code : ok -> jalar name, en ves de description is name
    # Description : add custom field
    # Stock UOM : ok
    # Required Qty : custom field?
    # Warehouse : ok
    # Quantity Requested for Purchase : custom field ?
    # Ordered Qty : ok
    # Actual Qty : ok

# Basado en la fecha de posting del DT