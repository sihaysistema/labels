# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		"Labels": {
			"color": "#F7DC6F",
			"icon": "assets/labels/images/barcode.svg",
			"type": "module",
			"label": _("Labels")
		}
	}

	# return [
	# 	{
	# 		"module_name": "Labels",
	# 		"color": "#0991DA",
	# 		"icon": "assets/labels/images/barcode.svg",
	# 		"type": "module",
	# 		"label": _("Labels")
	# 	}
	# ]
