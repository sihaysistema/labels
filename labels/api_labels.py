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
from labels.resources.label_setup import purchase_receipt_labels_pdf, delivery_note_labels_pdf


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
def purchase_receipt_labels(dict_data, label_format, receipt_date):
    """
        Description:
            Calls the creation of a PDF with serialized labels for items being received into inventory.
        Arguments:
        dict_data: 
            List item from the items child table in the purchase receipt, containing multiple
            objects / dictionaries with key:value pairs.
        label_format:
            Preset specification to access the label_config.json file that helps generate your own label type
        receipt_date:
            Posting date for purchase receipt.
    """

    # Carga como json-diccionario la data recibida
    selected_items = json.loads(dict_data)
    # frappe.msgprint(_(str(selected_items2)))
    # en_US: Declare a unique labels to print list, which will be filled with objects containing item name and serial number.
    unique_labels_to_print = []
    # en_US: First we loop through each purchase receipt item in the item_list, as user might have several item lines.
    for purchase_receipt_item in selected_items:
        # en_US: The serial number magic happens here. We get the contents and split the lines up. Each line is one serial number!
        unique_serial_no = purchase_receipt_item["serial_no"].split('\n')
        # en_US: Now we can loop through these unique serial numbers, and we create the objects that will change the look on our label.
        for serial_no in unique_serial_no:
            label_contents = {
                "item_name": purchase_receipt_item["item_name"],
                "serial_no": serial_no
                }
            # en_US: Append to the list.
            unique_labels_to_print.append(label_contents)

    # Guardara n items, cada item corresponde a una etiqueta

    # en_US: We call the labels PDF creation function, which needs a list of the items needed, the sticker type 1 of 4, production date, expiration date
    # es: Llamamos a la funcion de creacion del PDF de etiquetas, que necesita una lista de los codigos, el tipo de sticker 1 de 4, la fecha de produccion y la fecha de vencimiento.
    label_file_status = purchase_receipt_labels_pdf(unique_labels_to_print, receipt_date, label_format)
   
    # create_file_doctype_and_attach()

    # en_US: The value returnes is the URL location of the file, generated as a public file.
    # es: El valor retornado es la url ubicacion del archivo ya generado como publico
    return label_file_status

@frappe.whitelist()
def delivery_note_labels(dict_data, label_format, receipt_date):
    """
        Description:
            Calls the creation of a PDF with serialized labels for items to
            be delivered to a customer.
        Arguments:
        dict_data: 
            List item from the items child table in the purchase receipt, containing multiple
            objects / dictionaries with key:value pairs.
        label_format:
            Preset specification to access the label_config.json file that helps generate your own label type
        receipt_date:
            Posting date for purchase receipt.
    """

    # Carga como json-diccionario la data recibida
    selected_items = json.loads(dict_data)
    # frappe.msgprint(_(str(selected_items2)))
    # en_US: Declare a unique labels to print list, which will be filled with objects containing item name and serial number.
    unique_labels_to_print = []
    # en_US: First we loop through each purchase receipt item in the item_list, as user might have several item lines.
    for delivery_note_item in selected_items:
        # en_US: The serial number magic happens here. We get the contents and split the lines up. Each line is one serial number!
        unique_serial_no = delivery_note_item["serial_no"].split('\n')
        # en_US: Now we can loop through these unique serial numbers, and we create the objects that will change the look on our label.
        for serial_no in unique_serial_no:
            label_contents = {
                "item_name": delivery_note_item["item_name"],
                "serial_no": serial_no
                }
            # en_US: Append to the list.
            unique_labels_to_print.append(label_contents)

    # Guardara n items, cada item corresponde a una etiqueta

    # en_US: We call the labels PDF creation function, which needs a list of the items needed, the sticker type 1 of 4, production date, expiration date
    # es: Llamamos a la funcion de creacion del PDF de etiquetas, que necesita una lista de los codigos, el tipo de sticker 1 de 4, la fecha de produccion y la fecha de vencimiento.
    label_file_status = delivery_note_labels_pdf(unique_labels_to_print, receipt_date, label_format)
   
    # create_file_doctype_and_attach()

    # en_US: The value returnes is the URL location of the file, generated as a public file.
    # es: El valor retornado es la url ubicacion del archivo ya generado como publico
    return label_file_status
