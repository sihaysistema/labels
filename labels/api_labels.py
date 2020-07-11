# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import os, sys
import csv
import json
from datetime import datetime, date
from frappe.utils import get_site_name

from labels.resources.pdf_sticker_generator import crear_etiqueta

# This method is for debugging purposes only!
@frappe.whitelist()
def test_method(sticker_type):
    return "https://www.google.com/"

@frappe.whitelist()
def child_table_to_csv(dict_data, sticker_type, production_date, expiration_date):
    '''Procesa la data y cantidad para generacion de sticker'''

    # Carga como json-diccionario la data recibida
    dict_data_csv = json.loads(dict_data)

    # Guardara n items, cada item corresponde a una etiqueta
    listado_items = []

    for item in dict_data_csv:
        cantidad = item['planned_qty']

        for i in range(cantidad):
            parseo_codigo = str(item['item_code'])

            # Obtiene el nombre de cada item iterado
            nombre = frappe.get_value('Item', parseo_codigo, 'item_name')

            # tupla_d = (item['item_name'], parseo_codigo[(len(parseo_codigo) - 13):])
            # Por cada sticker crea una tupla con el nombre del item, y el barcode EAN13
            # Asumiendo que acada item code procesado al final tiene lo 13 digitos sin separacion
            tupla_d = (nombre, parseo_codigo[(len(parseo_codigo) - 13):])
            listado_items.append(tupla_d)

    # El valor retornado es la url ubicacion del archivo ya generado como publico
    # La ubicacion puede ser modificada
    status_etiqueta = crear_etiqueta(listado_items, sticker_type, production_date, expiration_date)

    return status_etiqueta
