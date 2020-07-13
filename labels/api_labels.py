# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import os, sys
import csv
import json
from datetime import datetime, date
from frappe.utils import get_site_name

from labels.resources.pdf_sticker_generator import create_labels_pdf, create_file_doctype_and_attach
from labels.resources.label_setup import new_create_labels_pdf


# This method is for debugging purposes only!
"""
@frappe.whitelist()
def test_method(sticker_type):
    return "https://www.google.com/"
"""

@frappe.whitelist()
def process_labels(dict_data, sticker_type, production_date, expiration_date):
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

    # en_US: We call the labels PDF creation function, which needs a list of the items needed, the sticker type 1 of 4, production date, expiration date
    # es: Llamamos a la funcion de creacion del PDF de etiquetas, que necesita una lista de los codigos, el tipo de sticker 1 de 4, la fecha de produccion y la fecha de vencimiento.
    label_file_status = create_labels_pdf(listado_items, sticker_type, production_date, expiration_date)
   
    # create_file_doctype_and_attach()

    # en_US: The value returnes is the URL location of the file, generated as a public file.
    # es: El valor retornado es la url ubicacion del archivo ya generado como publico
    return label_file_status

@frappe.whitelist()
def process_labels_2(dict_data, sticker_type, production_date, expiration_date):
    result = new_create_labels_pdf()
    return result

@frappe.whitelist()
def process_labels3(dict_data, sticker_type, production_date, expiration_date):
    '''Procesa la data y cantidad para generacion de sticker'''

    # Carga como json-diccionario la data recibida
    selected_items = json.loads(dict_data)

    # Guardara n items, cada item corresponde a una etiqueta
    item_list = []

    for item in selected_items:
        quantity = item['planned_qty']

        for i in range(quantity):
            parseo_codigo = str(item['item_code'])

            # Obtiene el nombre de cada item iterado
            nombre = frappe.get_value('Item', parseo_codigo, 'item_name')

            # tupla_d = (item['item_name'], parseo_codigo[(len(parseo_codigo) - 13):])
            # Por cada sticker crea una tupla con el nombre del item, y el barcode EAN13
            # Asumiendo que acada item code procesado al final tiene lo 13 digitos sin separacion
            tupla_d = (nombre, parseo_codigo[(len(parseo_codigo) - 13):])
            item_list.append(tupla_d)

    # en_US: We call the labels PDF creation function, which needs a list of the items needed, the sticker type 1 of 4, production date, expiration date
    # es: Llamamos a la funcion de creacion del PDF de etiquetas, que necesita una lista de los codigos, el tipo de sticker 1 de 4, la fecha de produccion y la fecha de vencimiento.
    label_file_status = new_create_labels_pdf(item_list, sticker_type, production_date, expiration_date)
   
    # create_file_doctype_and_attach()

    # en_US: The value returnes is the URL location of the file, generated as a public file.
    # es: El valor retornado es la url ubicacion del archivo ya generado como publico
    return label_file_status
