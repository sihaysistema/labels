# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import os, sys
import json
from datetime import datetime, date
from frappe.utils import get_site_name

# Element position for barcode begin from bottom left of "canvas" box.
# Higher height number move the element up, lower height number move the element down.
# Higher width numbers move the element to the right, lower width numbers move the element left.


# We open the configuration JSON
# We open the configuration JSON file  TODO: Some of this must be replaced with data from database, for development purposes only.

def new_create_labels_pdf():
    data = json.loads(open(frappe.get_app_path("labels", "resources", "labels_config.json")).read())
    labels = data["labels"]
    printers = data["printers"]
    label1 = labels["tunart-incoming-tuna"]["label_name"]
    label2 = labels["tunart-outgoing-tuna"]["label_name"]
    return label1

