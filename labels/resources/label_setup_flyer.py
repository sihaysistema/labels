# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import PIL
import os, sys
import locale
locale.setlocale(locale.LC_ALL, str('en_US.UTF-8'))
import hashlib, base64, string, json, pytz
import datetime
import traceback
# from datetime import datetime, date
from frappe.utils import get_site_name, get_site_path, get_bench_path

from six import text_type, PY2, string_types

from frappe.utils import get_site_name

# 1.2.2.1 Reportlab Graphics
# from reportlab.graphics.barcode import code39, code128, code93, qr, usps
# Constructor formulas are located here: reportlab.graphics.barcode.eanbc.py
from reportlab.graphics.barcode import eanbc, qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF  # To Render the PDF

# 1.2.2.2 Reportlab lib
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm # Converts mm to points.
from reportlab.lib import colors # Color management
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
# from reportlab.lib.utils import ImageReader

# 1.2.2.3 Reportlab pdfgen PDF Generator canvas. Where we will "draw" our pdf document.
from reportlab.pdfgen import canvas

# 1.2.2.4 Reportlab pdfmetric, TTFont  (to enable your own font)  FIXME
# Functions calling these are not working  FIXME
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 1.2.2.5 platypus
from reportlab.platypus import Paragraph # Paragraph style from reportlab

# 1.3 Babel modules
# sudo pip install babel
from babel import Locale
from babel.dates import UTC, format_date, format_datetime, format_time, get_timezone
from babel.numbers import format_number, format_decimal, format_percent
# Element position for barcode begin from bottom left of "canvas" box.
# Higher height number move the element up, lower height number move the element down.
# Higher width numbers move the element to the right, lower width numbers move the element left.
# We open the configuration JSON file  TODO: Some of this must be replaced with data from database, for development purposes only.

def purchase_receipt_labels_pdf(unique_item_list, receipt_date, selected_label_format="incoming_serial_no"):
    """
    selected_label_format = Must be an existing label_formats item in label_config.json!!!!!
    """

    #######################################################################################
    #
    #   1. Get date and time, create filename, site name, server file path, fonts and images.
    #
    #######################################################################################
    # 1.1 Using pytz to get current time including time zone.
    time_now_timezone = datetime.datetime.now(pytz.timezone(frappe.db.get_single_value('System Settings', 'time_zone'))).strftime("%Y-%m-%d-%H-%M-%S")
    # 1.2 Using standard datetime module, UTC time.
    # file_datetime = format_datetime(datetime.datetime.now(), "yyyy-MM-dd-kk-mm-ss", locale='es_GT')
    date_time_fileName_PDF_w_ext = 'Label-' + time_now_timezone + ".pdf"
    # 1.3 Get the site name and server file path where file will be stored.
    site_name = get_site_name(frappe.local.site)
    server_file_path = f'{site_name}/public/files/pdflabels/'
    # 1.4 Load fonts from the /public files.
    # load_font_roboto = "/resources/fonts/Roboto-Regular.ttf"
    load_font_roboto = frappe.get_app_path("labels", "public", "fonts", "Roboto-Regular.ttf")
    # 1.5 Load image for use in generating logo /public files.
    try:
        image_logo_filename = frappe.get_app_path("tunart", "public", "images" , "barcodelogo.jpg")
    except:
        image_logo_filename = "not found"
    # image_logo = "barcodelogo.jpg"
    # frappe.msgprint(_(image_logo_filename))

    try:

        #######################################################################################
        #
        #   2. Open labels_config.json and extract values for use in our script.
        #
        #######################################################################################
        # en_US: We load the label configuration JSON file
        label_config_file = "labels_config.json"
        data = json.loads(open(frappe.get_app_path("labels", "resources", label_config_file)).read())

        # en_US: We assign the contents of each individual section to the label_formats, colors, styles variable.
        label_formats = data["label_formats"]
        label_colors = data["label_colors"]
        label_styles = data["label_styles"]

        # frappe.msgprint(_("Success2"))
        #######################################################################################
        #
        #   3. We choose the style to be used
        #
        #######################################################################################
        # en_US: We create an object containing the selected label format, for access in for loop below
        this_label_format = label_formats[selected_label_format]
        # frappe.msgprint(_("Success3"))
        #######################################################################################
        #
        #   4. Page size / label size / margins
        #
        #######################################################################################
        # 4.1 GENERAL USER MODIFIABLE VARIABLES.
        # These variables represent the most important properties of the label.
        # We begin with the page or label size in millimeters.
        #--------------------------------------------------------------------------------------
        #  IMPORTANT NOTE ABOUT LABEL PRINTING!!!
        # Label printers use the x axis as the width, same here.
        # As a general rule, the widest part of the label will be also the x axis.
        # Do not alter the orientation aspects of labels when printing, print as portrait!
        label_height_mm = label_formats[selected_label_format]["label_height_mm"]
        label_width_mm = label_formats[selected_label_format]["label_width_mm"]
        #Left margin in mm (helps to wrap paragraph lines)
        lft_mgn = label_formats[selected_label_format]["margins"]["left_mm"]
        #Right margin in mm (helps to wrap paragraph lines)
        rgt_mgn = label_formats[selected_label_format]["margins"]["right_mm"]
        # frappe.msgprint(_("Success4"))
        #######################################################################################
        #
        #   5. Fixed Variables for labels (Days until expiration, field text, etc.)
        #
        #######################################################################################
        # FIXME FIXME FIXME FIXME FIXME
        # FIXME FIXME FIXME FIXME FIXME 
        # FIXME FIXME FIXME FIXME FIXME
        # FIXME FIXME FIXME FIXME FIXME
        #No extra spaces, the string concatenators will handle that.  Just the data.
        #test_bar_code = "1234567800069"
        #test_prod_desc = "Pillow Case Large"
        #test_prod_weight = "20"
        #test_prod_unit = "Oz."
        line3_produced_date_text = "Cosecha:"
        line4_expiration_date_text = "Vence:"
        days_to_expiration = 7
        currency_symb = "Q"
        test_price = 30.05                                       #Price not larger than Q99,000

        below_barcode_string = 'Hidropónico Sostenible. Puro'

        #######################################################################################
        #
        #   6. Colors
        #
        #######################################################################################
        # 6.1 Desired colors in RGB value o to 255
        rgb_pantone_3005_c_blue = (0,117,201)
        rgb_pantone_360_c_green = (108,192,74)
        rgb_pantone_000_c_white = (255,255,255)
        rgb_pantone_black = (0,0,0)

        # 6.2 Desired colors in HEX, obtained from the colors item list.
        hex_pantone_3005_c_blue = label_colors["hex_pantone_3005_c_blue"] 
        hex_pantone_360_c_green = label_colors["hex_pantone_360_c_green"]
        hex_pantone_000_c_white = label_colors["hex_pantone_000_c_white"]
        hex_pantone_black = label_colors["hex_pantone_black"]

        # 6.3 Convert colors to intensity mode 0- 100%
        rgb_pantone_black_int_red = rgb_pantone_black[0]/float(255)
        rgb_pantone_black_int_grn = rgb_pantone_black[1]/float(255)
        rgb_pantone_black_int_blu = rgb_pantone_black[2]/float(255)

        rgb_pantone_3005_c_blue_int_red = rgb_pantone_3005_c_blue[0]/float(255)
        rgb_pantone_3005_c_blue_int_grn = rgb_pantone_3005_c_blue[1]/float(255)
        rgb_pantone_3005_c_blue_int_blu = rgb_pantone_3005_c_blue[2]/float(255)

        # 6.3 bar color assignment
        bar_red = rgb_pantone_black_int_red
        bar_grn = rgb_pantone_black_int_grn
        bar_blu = rgb_pantone_black_int_blu
        # 6.4 text color assignment
        txt_red = rgb_pantone_black_int_red
        txt_grn = rgb_pantone_black_int_grn
        txt_blu = rgb_pantone_black_int_blu
        # 6.5 bar_stroke_color assignment
        stk_red = rgb_pantone_black_int_red
        stk_grn = rgb_pantone_black_int_grn
        stk_blu = rgb_pantone_black_int_blu
        # frappe.msgprint(_("Success6"))
        #######################################################################################
        #
        #   7. Move everything by x or y mm
        #
        #######################################################################################
        # 8.1 This moves everything by the specified mm. Useful for adjustments on the fly!
        # en_US:  This is sourced form the label style JSON.  Make changes to that JSON.
        # x axis + moves to right, - moves to left
        # y axis + moves up, - moves down
        # TODO:  Not working, must be included in every measurement insertion.
        move_x_mm = label_formats[selected_label_format]["move_x_mm"]
        move_y_mm = label_formats[selected_label_format]["move_y_mm"]

        #######################################################################################
        #
        #   8. Rotate everything 90 deg to the right, upside down, 90 to the left TODO: Pending!
        #
        #######################################################################################

        #######################################################################################
        #
        #   9. Positions of elements on page
        #
        #######################################################################################
        # 10.1 Element Individual Starting Positions
        # Elements must be placed, measuring from bottom left of label.
        # The general structure is
        # lINE 1=  Product name and weight
        # LINE 2= Product name and wight continued
        # LINE 3= Produced:  (date of production)
        # LINE 4= Expires: (date of expiration)
        # BARCODE =   EAN-13 Barcode
        # LINE 5 = Price
        # TODO:  If nothing specified, an IF function should default to CENTERING EVERYTHING
        # In relation to the chosen page size below
        # with DEFAULTS!  For quick and easy setup.

        # 13.2 Product Text position
        prod_x_pos_mm = 1           # 51mm x 38mm default = 3
        prod_y_pos_mm = 30          # 51mm x 38mm default = 30

        # 13.3 "Date of production"
        line_3_x_pos_mm = 1             # 51mm x 38mm default = 3
        line_3_y_pos_mm = 25            # 51mm x 38mm default = 25

        # 13.4 "Expiration date"
        #This line is set at 12.4mm from x origin to align the ":" for easier reading.
        line_4_x_pos_mm = 10.4          # 51mm x 38mm default = 12.4
        line_4_y_pos_mm = 21            # 51mm x 38mm default = 21

        # 13.5 Barcode position
        barcode_x_pos_mm = 5            # 51mm x 38mm default = 7
        barcode_y_pos_mm = 5            # 51mm x 38mm default = 5

        # 13.6 Usually the price or another description goes here
        below_barcode_x_pos_mm = 3      # 51mm x 38mm default = 19 for centered price
        below_barcode_y_pos_mm = .5      # 51mm x 38mm default = 1

        # 13.7 a Small number that returns the label group amount.
        # If you print 40 labels for a particular code, you can serialize it
        # for ease of counting.
        label_series_x_pos_mm = 0       # 51mm x 38mm default = 0
        label_series_y_pos_mm = 0       # 51mm x 38mm default = 0

        # 13.8 logo position
        image_logo_x_pos_mm = 16       # 51mm x 38mm default = 0
        image_logo_y_pos_mm = 30       # 51mm x 38mm default = 0
        image_logo_height_mm = 5      # 51mm x 38mm default = 5
        # frappe.msgprint(_("Success9"))

        #######################################################################################
        #
        #   10. Barcode Style parameters
        #
        #######################################################################################
        # 10.1 FONTS Available fonts for the barcode human readable text
        # Helvetica, Mac expert, standard, symbol, winansi, zapfdingbats, courier, courier bold corierboldoblique courieroblique, helvetica bold, helvetica bold oblique, symbol, times bold times bold italic times italic timesroman zapfdingbats.
        # 10.2.1 Color. method. default = colors.black, or colors.Color(R,G,B,1), or colors.
        bar_fill_color = colors.Color(bar_red,bar_grn,bar_blu,alpha=1)
        # 10.2.2 Height, Width, stroke width
        bar_height_mm = 15                                              # Number. default =  13
        bar_width_mm = .41                                              # Number. default = .41
        bar_stroke_width = .05                                          # Number. default = .05
        # 10.2.3 Stroke Color. method. default = colors.black
        bar_stroke_color = colors.Color(stk_red,stk_grn,stk_blu,alpha=1)
        # 10.2.4 Human Readable text color. method. default = colors.black
        barcode_text_color = colors.Color(txt_red,txt_grn,txt_blu,alpha=1)

        """
        #Check this one out!
        http://pydoc.net/Python/reportlab/3.3.0/reportlab.graphics.barcode/
        """

        # frappe.msgprint(_("Success10"))
        #######################################################################################
        #
        #   11. Element Wrappers. in mm. Creates a "virtual box" so that text doesn't flow out
        #
        #######################################################################################

        prod_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        prod_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for line 3, so text cuts off rather than intrude elsewhere
        line_3_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        line_3_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for line 4, so text cuts off rather than intrude elsewhere
        line_4_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        line_4_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for line 4, so text cuts off rather than intrude elsewhere
        below_barcode_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        below_barcode_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for label series, so text cuts off rather than intrude elsewhere
        label_series_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        label_series_y_wrap_mm = label_height_mm-bar_height_mm
        
        # frappe.msgprint(_("Success11"))

        #######################################################################################
        #
        #   12. Program variables that involve flow control  CAREFUL!
        #
        #######################################################################################

        # 12.1  THE VALID PREFIX.  If you change this, no barcodes will be printed!
        # This prefix must be the one issued by GS1 or prefix issuing authority in your locality.
        valid_gs1_prefix = "74011688"
        # 12.2 Search string used right before product name
        # PLEASE NOTE: Label must be an Item in ERPNext, part of the Bill of Materials of the sales item, and the name must beign with this string, otherwise, the label will not be counted.
        desc_search_string = "Etiqueta Normal"
        # desc_ending_html = html_par_close

        # frappe.msgprint(_("Success12"))
        #######################################################################################
        #
        #   12. date calculations (default date is today)
        #
        #######################################################################################

        # 12.1 Date calculation and formatting.
        # default= today, or can be specified date(2016, 14, 11)
        # production_date = datetime.date.today()
        # production_date_print = format_date(production_date,"dd.LLLyyyy" ,locale='es_GT')
        # production_date_print = production_date

        # 12.2 Expiration date calculation and formatting
        #Calculates from the production date stated above.
        # expiration_date = production_date + datetime.timedelta(days=days_to_expiration) 
        # expiration_date = expiration_date
        # expiration_date_print = format_date(expiration_date,"dd.LLLyyyy" ,locale='es_GT')
        # expiration_date_print = expiration_date

        # frappe.msgprint(_("Success12"))
        #######################################################################################
        #
        #   13. Currency formatting
        #
        #######################################################################################

        #13.1 Using python string formatting 
        #test_price_str = str("%0.2f" % test_price)  # no commas
        # below format with commas and two decimal points.
        #test_format_price = locale.format("%0.2f",test_price, grouping=True)
        format_price_print = format_decimal(test_price, format='#,##0.##;-#', locale='es_GT')
        # frappe.msgprint(_("Success13"))
        ######################################################
        #
        #   14. mm to point converter
        #
        ######################################################
        """
        For our label, the position must be specified in points.  Above the user enters the 
        values in mm, and these will convert from mm to points.  The move_x_mm and move_y_mm
        will shift the position of all the items in the label together, when specified by the user.

        """
        bar_width = bar_width_mm*mm
        bar_height = bar_height_mm*mm

        below_barcode_x_pos = (below_barcode_x_pos_mm+move_x_mm)*mm
        below_barcode_y_pos = (below_barcode_y_pos_mm+move_y_mm)*mm

        label_series_x_pos = (label_series_x_pos_mm+move_x_mm)*mm
        label_series_y_pos = (label_series_y_pos_mm+move_y_mm)*mm

        image_logo_x_pos = (image_logo_x_pos_mm+move_x_mm)*mm
        image_logo_y_pos = (image_logo_y_pos_mm+move_y_mm)*mm

        prod_x_wrap = (prod_x_wrap_mm+move_x_mm)*mm
        prod_y_wrap = (prod_y_wrap_mm+move_y_mm)*mm

        line_3_x_wrap = (line_3_x_wrap_mm+move_x_mm)*mm
        line_3_y_wrap = (line_3_y_wrap_mm+move_y_mm)*mm

        line_4_x_wrap = (line_4_x_wrap_mm+move_x_mm)*mm
        line_4_y_wrap = (line_4_y_wrap_mm+move_y_mm)*mm

        below_barcode_x_wrap = (below_barcode_x_wrap_mm+move_x_mm)*mm
        below_barcode_y_wrap = (below_barcode_y_wrap_mm+move_y_mm)*mm

        label_series_x_wrap = (label_series_x_wrap_mm+move_x_mm)*mm
        label_series_y_wrap = (label_series_y_wrap_mm+move_y_mm)*mm

        image_logo_height = (image_logo_height_mm+move_y_mm)*mm
        # frappe.msgprint(_("Success14"))
        ######################################################
        #
        #   15. Concatenating the text strings
        #
        ######################################################
        #15.1 Concatenating the Strings required by the label.
        line_3_text = line3_produced_date_text + "" #production_date_print
        line_4_text = line4_expiration_date_text + "" #expiration_date_print 
        below_barcode_text = below_barcode_string #currency_symb + format_price_print
        # frappe.msgprint(_("Success15"))
        ###################################################################################
        #
        #   16. Create a Canvas PDF object to contain everything. One PDF canvas per page.
        #
        ###################################################################################
        """
        Create a PDFCanvas object where we will deposit all the  elements of the PDF.
        drawing object, and then add the barcode to the drawing. Add styles to platypus style.
        Then using renderPDF, you place the drawing on the PDF. Finally, you save the file.
        """
        PDFcanvas = canvas.Canvas((str(server_file_path) + str(date_time_fileName_PDF_w_ext)))
        PDFcanvas.setPageSize((label_width_mm*mm, label_height_mm*mm))
        # frappe.msgprint(_("Success16"))
        ###################################################################################
        #
        #   17. Apply paragraph styles for entire document
        #
        ###################################################################################
        # en_US: Create a stylesheet object instance
        load_label_styles = getSampleStyleSheet()
        # en_US: Iterate over each style included in the label_config.json and make it available for our PDF generation purposes.
        for each_style in label_styles:
            load_label_styles.add(ParagraphStyle(name=each_style["name"], fontName=each_style["fontName"], fontSize=each_style["fontSize"], leading=each_style["leading"], leftIndent=each_style["leftIndent"], rightIndent=each_style["rightIndent"], firstLineIndent=each_style["firstLineIndent"], alignment=each_style["alignment"], spaceBefore=each_style["spaceBefore"], spaceAfter=each_style["spaceAfter"], bulletFontName=each_style["bulletFontName"], bulletFontSize=each_style["bulletFontSize"], bulletIndent=each_style["bulletIndent"], textColor=each_style["textColor"], backColor=each_style["backColor"], wordWrap=each_style["wordWrap"], borderWidth=each_style["borderWidth"], borderPadding=each_style["borderPadding"], borderColor=each_style["borderColor"], borderRadius=each_style["borderRadius"], allowWidows=each_style["allowWidows"], allowOrphans=each_style["allowOrphans"], textTransform=each_style["textTransform"], endDots=each_style["endDots"], splitLongWords=each_style["splitLongWords"]))
            # frappe.msgprint(_("Success17"))
        ###################################################################################
        #
        #   18. Set the FONT load_font_roboto = font_path + "roboto/Roboto-Regular.ttf"
        #   FIXME
        ###################################################################################
        #barcode_font = r"/fonts/roboto/RobotoRegular.ttf"
        #barcode_font = "fonts/roboto/RobotoRegular.ttf" FIXME
        #pdfmetrics.registerFont(TTFont('vera','RobotoRegular.ttf'))
        receipt1_date = "13-07-2020"
        ###################################################################################
        #
        #   19. Loop through the list creating the individual labels
        #
        ###################################################################################
        # The enumerate function allows access to the list or dictionary items while the for loop iterates
        for index, each_label_object in enumerate(unique_item_list):
            # Index variable is initiated above, and returns the index or position of the list item being iterated.
            # print("this is the index: " + str(index))
            # each_label_tuple is initiated above, and is usedby enumerate to return the
            # contents of the current list item being iterated.
            #print("this is the tuple item: " + str(each_label_tuple))

            ###############################################################################
            #
            #   19.2 Set the text fill color for strings
            #
            ###############################################################################
            
            PDFcanvas.setFillColorRGB(txt_red,txt_grn,txt_blu) #choose your font color
            # frappe.msgprint(_("Success19.2"))
            ###############################################################################
            #
            #   19.3 Create the individual page using the same size as the label indicated above
            #
            ###############################################################################
            # en_US: Creates a page drawing object for each label.
            # page = Drawing(label_width_mm*mm, label_height_mm*mm)
            # frappe.msgprint(_("Success19.3A"))
            for element in this_label_format["elements"]:
                # en_US: We check which type of element we need to draw
                if element["element_type"] == "receipt_date":
                    # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                    PDFcanvas.setFont(element["font_name"], 20)
                    PDFcanvas.drawString(element["x_pos_mm"]*mm, element["y_pos_mm"]*mm, receipt_date)
                elif element["element_type"] == "item_name":
                    # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                    PDFcanvas.setFont('Helvetica', 20)
                    PDFcanvas.drawString(element["x_pos_mm"]*mm, element["y_pos_mm"]*mm, each_label_object["item_name"])
                elif element["element_type"] == "serial_no":
                    # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                    PDFcanvas.setFont('Helvetica', 20)
                    serial_no_txt = _("Serial No: ") + each_label_object["serial_no"]
                    PDFcanvas.drawString(element["x_pos_mm"]*mm, element["y_pos_mm"]*mm, serial_no_txt)
                elif element["element_type"] == "paragraph":
                    ###############################################################################
                    #
                    #   13.4.? Add the Product description as a paragraph
                    #
                    ###############################################################################
                    frappe.msgprint(_("Success-ISTEXT"))
                    label_prod_desc_area = Paragraph(curr_tuple_label_desc, style=label_styles["Blue"])
                    label_prod_desc_area.wrapOn(PDFcanvas, prod_x_wrap, prod_y_wrap)
                    label_prod_desc_area.drawOn(PDFcanvas, prod_x_pos, prod_y_pos, mm)

                    ###############################################################################
                    #
                    #   13.4.? Add line 3 (below Prod description 1 or 2 lines) as a paragraph
                    #
                    ###############################################################################

                    # No Mostrara las fechas
                    if sticker_type == '0':
                        pass

                    # Mostrara unicamente la fecha de cosecha
                    if sticker_type == '1':
                        label_line3_area = Paragraph(line_3_text, style=styles["line3"])
                        label_line3_area.wrapOn(PDFcanvas, line_3_x_wrap, line_3_y_wrap)
                        label_line3_area.drawOn(PDFcanvas, line_3_x_pos, line_3_y_pos, mm)

                    # Mostrara unicamente la fecha de vencimiento
                    if sticker_type == '2':
                        label_line4_area = Paragraph(line_4_text, style=styles["line4"])
                        label_line4_area.wrapOn(PDFcanvas, line_4_x_wrap, line_4_y_wrap)
                        label_line4_area.drawOn(PDFcanvas, line_4_x_pos, line_4_y_pos, mm)

                    if sticker_type == '3':
                        label_line3_area = Paragraph(line_3_text, style=styles["line3"])
                        label_line3_area.wrapOn(PDFcanvas, line_3_x_wrap, line_3_y_wrap)
                        label_line3_area.drawOn(PDFcanvas, line_3_x_pos, line_3_y_pos, mm)

                        label_line4_area = Paragraph(line_4_text, style=styles["line4"])
                        label_line4_area.wrapOn(PDFcanvas, line_4_x_wrap, line_4_y_wrap)
                        label_line4_area.drawOn(PDFcanvas, line_4_x_pos, line_4_y_pos, mm)

                    #PDFcanvas.setFont('vera', 32)
                    #This draws the text strings, gets position numbers from variables at beggining of file.

                    """ OPTIONAL IF YOU REGISTER A BARCODE FONT, THIS IS ANOTHER WAY TO SET IT UP
                    barcode_string = '<font name="Free 3 of 9 Regular" size="12">%s</font>'
                        barcode_string = barcode_string % "1234567890"
                    """
                    #line_1_and_2 = '<font name="Helvetica" size="12">%s</font>'
                    #line_1_and_2 = line_1_and_2 % line_1_txt

                elif element["element_type"] == "ean13barcode":
                    # 7.4 Defining the quiet space value
                    #if barcode_use_quiet_space == 'yes':
                    #    quiet_space = 'TRUE'

                    ###############################################################################
                    #
                    #   19.2.1 Obtain the contents of the unique label list tuples
                    #
                    ###############################################################################
                    curr_tuple_label_desc = str(each_label_tuple[0])
                    curr_tuple_label_barcode = str(each_label_tuple[1])
                    #print("Current Code from tuple: " + curr_tuple_label_barcode)
                    #print("Current Product from tuple: " + curr_tuple_label_desc)

                    ###############################################################################
                    #
                    #   19.2.2 Draw the EAN-13 Code
                    #
                    ###############################################################################
                    # Pass barcode creation parameters to reportlab, any order, as name=value pairs.
                    # Order may be changed, since reportlab maps name=value pairs automatically.
                    # Source code for ordering
                    # http://pydoc.net/Python/reportlab/3.3.0/reportlab.graphics.barcode.eanbc/

                    barcode_eanbc13 = eanbc.Ean13BarcodeWidget(value=curr_tuple_label_barcode,fontName=element["fontName"],fontSize=element["fontSize"],x=element["x_pos_mm"]*mm,y=element["y_pos_mm"]*mm,barFillColor=bar_fill_color,barHeight=element["barHeight"],barWidth=element["barWidth"],barStrokeWidth=element["barStrokeWidth"],barStrokeColor=bar_stroke_color,textColor=barcode_text_color,humanReadable=element["humanReadable"],quiet=element["quiet"],lquiet=element["lquiet"],rquiet=element["rquiet"])

                    ###############################################################################
                    #
                    #   13.4.? Add the barcode and position it on the PDFcanvas
                    #
                    ###############################################################################
                    page.add(barcode_eanbc13)
                    # Place the generated barcode on the page.
                    # (Drawing object, Barcode object, x position, y position)
                    renderPDF.draw(page, PDFcanvas, 0, 0)

                elif element["element_type"] == "logo_image" and image_logo_filename != "not found":
                    try:
                        PDFcanvas.drawImage(image_logo_filename, int(element["x_pos_px"]), int(element["y_pos_px"]), width=None,height=int(element["height_px"]),mask=None,preserveAspectRatio=True)
                        # PDFcanvas.drawImage(image_logo_filename, element["x_pos_mm"]*mm, element["y_pos_mm"]*mm, width=None, height='30', mask=None, preserveAspectRatio=True,  anchor='c')
                    except:
                        frappe.msgprint(_("Could not draw image")+str(frappe.get_traceback()))
                        """
                        elif element["element_type"] == "qrcode":
                            # draw qrcode
                        """

            # For every Label Item, we must show the page.
            PDFcanvas.showPage()
        
        # frappe.msgprint(_("Before if"))
        if os.path.exists(server_file_path):
            PDFcanvas.save()
        else:
            # This portion creates the folder where the sticker file will be saved to.
            frappe.create_folder(server_file_path)
            # This portion creates the folder and saves it to the sites directory specified.
            PDFcanvas.save()

        # en_US:  We want to return the URL of the file directly for download in ERPNext.
        file_url = f'files/pdflabels/{date_time_fileName_PDF_w_ext}'

        # return file_url
        return file_url

    except:
        # exception_message = _("Label configuration script could not be loaded. Please check ") + label_config_file
        exception_message = _("Label creation failed")

        return exception_message

def delivery_note_flyers_pdf(unique_item_list, receipt_date, selected_label_format="incoming_serial_no"):
    """
    selected_label_format = Must be an existing label_formats item in label_config.json!!!!!
    """

    #######################################################################################
    #
    #   1. Get date and time, create filename, site name, server file path, fonts and images.
    #
    #######################################################################################
    # 1.1 Using pytz to get current time including time zone.
    time_now_timezone = datetime.datetime.now(pytz.timezone(frappe.db.get_single_value('System Settings', 'time_zone'))).strftime("%Y-%m-%d-%H-%M-%S")
    # 1.2 Using standard datetime module, UTC time.
    # file_datetime = format_datetime(datetime.datetime.now(), "yyyy-MM-dd-kk-mm-ss", locale='es_GT')
    date_time_fileName_PDF_w_ext = 'Label-' + time_now_timezone + ".pdf"
    # 1.3 Get the site name and server file path where file will be stored.
    site_name = get_site_name(frappe.local.site)
    server_file_path = f'{site_name}/public/files/pdflabels/'
    # 1.4 Load fonts from the /public files.
    # load_font_roboto = "/resources/fonts/Roboto-Regular.ttf"
    load_font_roboto = frappe.get_app_path("labels", "public", "fonts", "Roboto-Regular.ttf")
    # 1.5 Load image for use in generating logo /public files.
    try:
        image_logo_filename = frappe.get_app_path("tunart", "public", "images" , "barcodelogo.jpg")
    except:
        image_logo_filename = "not found"
    tunart_url = "https://www.tunart.biz"
    # image_logo = "barcodelogo.jpg"
    # frappe.msgprint(_(image_logo_filename))

    try:

        #######################################################################################
        #
        #   2. Open labels_config.json and extract values for use in our script.
        #
        #######################################################################################
        # en_US: We load the label configuration JSON file
        label_config_file = "labels_config.json"
        data = json.loads(open(frappe.get_app_path("labels", "resources", label_config_file)).read())

        # en_US: We assign the contents of each individual section to the label_formats, colors, styles variable.
        label_formats = data["label_formats"]
        label_colors = data["label_colors"]
        label_styles = data["label_styles"]

        #frappe.msgprint(_("Success2"))
        #######################################################################################
        #
        #   3. We choose the style to be used
        #
        #######################################################################################
        # en_US: We create an object containing the selected label format, for access in for loop below
        this_label_format = label_formats[selected_label_format]
        # frappe.msgprint(_("Success3"))
        #######################################################################################
        #
        #   4. Page size / label size / margins
        #
        #######################################################################################
        # 4.1 GENERAL USER MODIFIABLE VARIABLES.
        # These variables represent the most important properties of the label.
        # We begin with the page or label size in millimeters.
        #--------------------------------------------------------------------------------------
        #  IMPORTANT NOTE ABOUT LABEL PRINTING!!!
        # Label printers use the x axis as the width, same here.
        # As a general rule, the widest part of the label will be also the x axis.
        # Do not alter the orientation aspects of labels when printing, print as portrait!
        label_height_mm = label_formats[selected_label_format]["label_height_mm"]
        label_width_mm = label_formats[selected_label_format]["label_width_mm"]
        #Left margin in mm (helps to wrap paragraph lines)
        lft_mgn = label_formats[selected_label_format]["margins"]["left_mm"]
        #Right margin in mm (helps to wrap paragraph lines)
        rgt_mgn = label_formats[selected_label_format]["margins"]["right_mm"]
        #frappe.msgprint(_("Success4"))
        #######################################################################################
        #
        #   5. Fixed Variables for labels (Days until expiration, field text, etc.)
        #
        #######################################################################################
        # FIXME FIXME FIXME FIXME FIXME
        # FIXME FIXME FIXME FIXME FIXME 
        # FIXME FIXME FIXME FIXME FIXME
        # FIXME FIXME FIXME FIXME FIXME
        #No extra spaces, the string concatenators will handle that.  Just the data.

        #######################################################################################
        #
        #   6. Colors
        #
        #######################################################################################
        # 6.1 Desired colors in RGB value o to 255
        rgb_pantone_3005_c_blue = (0,117,201)
        rgb_pantone_360_c_green = (108,192,74)
        rgb_pantone_000_c_white = (255,255,255)
        rgb_pantone_black = (0,0,0)
        rgb_tunart_blue = (26/float(255), 110/float(255), 156/float(255))

        # 6.2 Desired colors in HEX, obtained from the colors item list.
        hex_pantone_3005_c_blue = label_colors["hex_pantone_3005_c_blue"] 
        hex_pantone_360_c_green = label_colors["hex_pantone_360_c_green"]
        hex_pantone_000_c_white = label_colors["hex_pantone_000_c_white"]
        hex_pantone_black = label_colors["hex_pantone_black"]

        # 6.3 Convert colors to intensity mode 0- 100%
        rgb_pantone_black_int_red = rgb_pantone_black[0]/float(255)
        rgb_pantone_black_int_grn = rgb_pantone_black[1]/float(255)
        rgb_pantone_black_int_blu = rgb_pantone_black[2]/float(255)

        rgb_pantone_3005_c_blue_int_red = rgb_pantone_3005_c_blue[0]/float(255)
        rgb_pantone_3005_c_blue_int_grn = rgb_pantone_3005_c_blue[1]/float(255)
        rgb_pantone_3005_c_blue_int_blu = rgb_pantone_3005_c_blue[2]/float(255)

        # 6.3 bar color assignment
        bar_red = rgb_pantone_black_int_red
        bar_grn = rgb_pantone_black_int_grn
        bar_blu = rgb_pantone_black_int_blu
        # 6.4 text color assignment
        txt_red = rgb_pantone_black_int_red
        txt_grn = rgb_pantone_black_int_grn
        txt_blu = rgb_pantone_black_int_blu
        # 6.5 bar_stroke_color assignment
        stk_red = rgb_pantone_black_int_red
        stk_grn = rgb_pantone_black_int_grn
        stk_blu = rgb_pantone_black_int_blu
        # frappe.msgprint(_("Success6"))
        #######################################################################################
        #
        #   7. Move everything by x or y mm
        #
        #######################################################################################
        # 8.1 This moves everything by the specified mm. Useful for adjustments on the fly!
        # en_US:  This is sourced form the label style JSON.  Make changes to that JSON.
        # x axis + moves to right, - moves to left
        # y axis + moves up, - moves down
        # TODO:  Not working, must be included in every measurement insertion.
        move_x_mm = label_formats[selected_label_format]["move_x_mm"]
        move_y_mm = label_formats[selected_label_format]["move_y_mm"]

        #######################################################################################
        #
        #   8. Rotate everything 90 deg to the right, upside down, 90 to the left TODO: Pending!
        #
        #######################################################################################

        #######################################################################################
        #
        #   9. Positions of elements on page
        #
        #######################################################################################
        # 10.1 Element Individual Starting Positions
        # Elements must be placed, measuring from bottom left of label.
        # The general structure is
        # lINE 1=  Product name and weight
        # LINE 2= Product name and wight continued
        # LINE 3= Produced:  (date of production)
        # LINE 4= Expires: (date of expiration)
        # BARCODE =   EAN-13 Barcode
        # LINE 5 = Price
        # TODO:  If nothing specified, an IF function should default to CENTERING EVERYTHING
        # In relation to the chosen page size below
        # with DEFAULTS!  For quick and easy setup.

        # 13.2 Product Text position
        prod_x_pos_mm = 1           # 51mm x 38mm default = 3
        prod_y_pos_mm = 30          # 51mm x 38mm default = 30

        # 13.3 "Date of production"
        line_3_x_pos_mm = 1             # 51mm x 38mm default = 3
        line_3_y_pos_mm = 25            # 51mm x 38mm default = 25

        # 13.4 "Expiration date"
        #This line is set at 12.4mm from x origin to align the ":" for easier reading.
        line_4_x_pos_mm = 10.4          # 51mm x 38mm default = 12.4
        line_4_y_pos_mm = 21            # 51mm x 38mm default = 21

        # 13.5 Barcode position
        barcode_x_pos_mm = 5            # 51mm x 38mm default = 7
        barcode_y_pos_mm = 5            # 51mm x 38mm default = 5

        # 13.6 Usually the price or another description goes here
        below_barcode_x_pos_mm = 3      # 51mm x 38mm default = 19 for centered price
        below_barcode_y_pos_mm = .5      # 51mm x 38mm default = 1

        # 13.7 a Small number that returns the label group amount.
        # If you print 40 labels for a particular code, you can serialize it
        # for ease of counting.
        label_series_x_pos_mm = 0       # 51mm x 38mm default = 0
        label_series_y_pos_mm = 0       # 51mm x 38mm default = 0

        # 13.8 logo position
        image_logo_x_pos_mm = 16       # 51mm x 38mm default = 0
        image_logo_y_pos_mm = 30       # 51mm x 38mm default = 0
        image_logo_height_mm = 5      # 51mm x 38mm default = 5
        #frappe.msgprint(_("Success9"))

        #######################################################################################
        #
        #   10. Barcode Style parameters
        #
        #######################################################################################
        # 10.1 FONTS Available fonts for the barcode human readable text
        # Helvetica, Mac expert, standard, symbol, winansi, zapfdingbats, courier, courier bold corierboldoblique courieroblique, helvetica bold, helvetica bold oblique, symbol, times bold times bold italic times italic timesroman zapfdingbats.
        # 10.2.1 Color. method. default = colors.black, or colors.Color(R,G,B,1), or colors.
        bar_fill_color = colors.Color(bar_red,bar_grn,bar_blu,alpha=1)
        # 10.2.2 Height, Width, stroke width
        bar_height_mm = 15                                              # Number. default =  13
        bar_width_mm = .41                                              # Number. default = .41
        bar_stroke_width = .05                                          # Number. default = .05
        # 10.2.3 Stroke Color. method. default = colors.black
        bar_stroke_color = colors.Color(stk_red,stk_grn,stk_blu,alpha=1)
        # 10.2.4 Human Readable text color. method. default = colors.black
        barcode_text_color = colors.Color(txt_red,txt_grn,txt_blu,alpha=1)

        """
        #Check this one out!
        http://pydoc.net/Python/reportlab/3.3.0/reportlab.graphics.barcode/
        """

        #frappe.msgprint(_("Success10"))
        #######################################################################################
        #
        #   11. Element Wrappers. in mm. Creates a "virtual box" so that text doesn't flow out
        #
        #######################################################################################

        prod_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        prod_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for line 3, so text cuts off rather than intrude elsewhere
        line_3_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        line_3_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for line 4, so text cuts off rather than intrude elsewhere
        line_4_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        line_4_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for line 4, so text cuts off rather than intrude elsewhere
        below_barcode_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        below_barcode_y_wrap_mm = label_height_mm-bar_height_mm

        #Create a wrapper for label series, so text cuts off rather than intrude elsewhere
        label_series_x_wrap_mm = label_width_mm-lft_mgn-rgt_mgn
        label_series_y_wrap_mm = label_height_mm-bar_height_mm
        
        # frappe.msgprint(_("Success11"))

        #######################################################################################
        #
        #   12. Program variables that involve flow control  CAREFUL!
        #
        #######################################################################################

        # 12.1  THE VALID PREFIX.  If you change this, no barcodes will be printed!
        # This prefix must be the one issued by GS1 or prefix issuing authority in your locality.
        valid_gs1_prefix = "74011688"
        # 12.2 Search string used right before product name
        # PLEASE NOTE: Label must be an Item in ERPNext, part of the Bill of Materials of the sales item, and the name must beign with this string, otherwise, the label will not be counted.
        desc_search_string = "Etiqueta Normal"
        # desc_ending_html = html_par_close

        #frappe.msgprint(_("Success12"))
        #######################################################################################
        #
        #   13. Currency formatting
        #
        #######################################################################################

        #13.1 Using python string formatting 
        #test_price_str = str("%0.2f" % test_price)  # no commas
        # below format with commas and two decimal points.
        #test_format_price = locale.format("%0.2f",test_price, grouping=True)
        # format_price_print = format_decimal(test_price, format='#,##0.##;-#', locale='es_GT')
        #frappe.msgprint(_("Success13"))
        ######################################################
        #
        #   14. mm to point converter
        #
        ######################################################
        """
        For our label, the position must be specified in points.  Above the user enters the 
        values in mm, and these will convert from mm to points.  The move_x_mm and move_y_mm
        will shift the position of all the items in the label together, when specified by the user.

        """
        bar_width = bar_width_mm*mm
        bar_height = bar_height_mm*mm

        below_barcode_x_pos = (below_barcode_x_pos_mm+move_x_mm)*mm
        below_barcode_y_pos = (below_barcode_y_pos_mm+move_y_mm)*mm

        label_series_x_pos = (label_series_x_pos_mm+move_x_mm)*mm
        label_series_y_pos = (label_series_y_pos_mm+move_y_mm)*mm

        image_logo_x_pos = (image_logo_x_pos_mm+move_x_mm)*mm
        image_logo_y_pos = (image_logo_y_pos_mm+move_y_mm)*mm

        prod_x_wrap = (prod_x_wrap_mm+move_x_mm)*mm
        prod_y_wrap = (prod_y_wrap_mm+move_y_mm)*mm

        line_3_x_wrap = (line_3_x_wrap_mm+move_x_mm)*mm
        line_3_y_wrap = (line_3_y_wrap_mm+move_y_mm)*mm

        line_4_x_wrap = (line_4_x_wrap_mm+move_x_mm)*mm
        line_4_y_wrap = (line_4_y_wrap_mm+move_y_mm)*mm

        below_barcode_x_wrap = (below_barcode_x_wrap_mm+move_x_mm)*mm
        below_barcode_y_wrap = (below_barcode_y_wrap_mm+move_y_mm)*mm

        label_series_x_wrap = (label_series_x_wrap_mm+move_x_mm)*mm
        label_series_y_wrap = (label_series_y_wrap_mm+move_y_mm)*mm

        image_logo_height = (image_logo_height_mm+move_y_mm)*mm
        #frappe.msgprint(_("Success14"))
        ######################################################
        #
        #   15. Concatenating the text strings
        #
        ######################################################
        #15.1 Concatenating the Strings required by the label.

        #frappe.msgprint(_("Success15"))
        ###################################################################################
        #
        #   16. Create a Canvas PDF object to contain everything. One PDF canvas per page.
        #
        ###################################################################################
        """
        Create a PDFCanvas object where we will deposit all the  elements of the PDF.
        drawing object, and then add the barcode to the drawing. Add styles to platypus style.
        Then using renderPDF, you place the drawing on the PDF. Finally, you save the file.
        """
        PDFcanvas = canvas.Canvas((str(server_file_path) + str(date_time_fileName_PDF_w_ext)))
        PDFcanvas.setPageSize((label_width_mm*mm, label_height_mm*mm))
        #frappe.msgprint(_("Success16"))
        ###################################################################################
        #
        #   17. Apply paragraph styles for entire document
        #
        ###################################################################################
        # en_US: Create a stylesheet object instance
        load_label_styles = getSampleStyleSheet()
        # en_US: Iterate over each style included in the label_config.json and make it available for our PDF generation purposes.
        for each_style in label_styles:
            load_label_styles.add(ParagraphStyle(name=each_style["name"], 
                                                 fontName=each_style["fontName"], 
                                                 fontSize=each_style["fontSize"], 
                                                 leading=each_style["leading"], 
                                                 leftIndent=each_style["leftIndent"], 
                                                 rightIndent=each_style["rightIndent"], 
                                                 firstLineIndent=each_style["firstLineIndent"], 
                                                 alignment=each_style["alignment"], 
                                                 spaceBefore=each_style["spaceBefore"], 
                                                 spaceAfter=each_style["spaceAfter"], 
                                                 bulletFontName=each_style["bulletFontName"], 
                                                 bulletFontSize=each_style["bulletFontSize"], 
                                                 bulletIndent=each_style["bulletIndent"], 
                                                 textColor=each_style["textColor"], 
                                                 backColor=each_style["backColor"], 
                                                 wordWrap=each_style["wordWrap"], 
                                                 borderWidth=each_style["borderWidth"], 
                                                 borderPadding=each_style["borderPadding"], 
                                                 borderColor=each_style["borderColor"], 
                                                 borderRadius=each_style["borderRadius"], 
                                                 allowWidows=each_style["allowWidows"], 
                                                 allowOrphans=each_style["allowOrphans"], 
                                                 textTransform=each_style["textTransform"], 
                                                 endDots=each_style["endDots"], 
                                                 splitLongWords=each_style["splitLongWords"]))
            #frappe.msgprint(_("Success17"))
        ###################################################################################
        #
        #   18. Set the FONT load_font_roboto = font_path + "roboto/Roboto-Regular.ttf"
        #   FIXME
        ###################################################################################
        #barcode_font = r"/fonts/roboto/RobotoRegular.ttf"
        #barcode_font = "fonts/roboto/RobotoRegular.ttf" FIXME
        #pdfmetrics.registerFont(TTFont('vera','RobotoRegular.ttf'))
        receipt1_date = "13-07-2020"
        ###################################################################################
        #
        #   19. Loop through the list creating the individual labels
        #
        ###################################################################################
        # The enumerate function allows access to the list or dictionary items while the for loop iterates
        for index, each_label_object in enumerate(unique_item_list):
            # Index variable is initiated above, and returns the index or position of the list item being iterated.
            # print("this is the index: " + str(index))
            # each_label_tuple is initiated above, and is usedby enumerate to return the
            # contents of the current list item being iterated.
            #print("this is the tuple item: " + str(each_label_tuple))

            ###############################################################################
            #
            #   19.2 Set the text fill color for strings
            #
            ###############################################################################
            
            PDFcanvas.setFillColorRGB(txt_red,txt_grn,txt_blu)
            #PDFcanvas.setFillColorRGB(*rgb_tunart_blue)
            # rgb_tunart_blue_bg #choose your font color
            # frappe.msgprint(_("Success19.2"))
            ###############################################################################
            #
            #   19.3 Create the individual page using the same size as the label indicated above
            #
            ###############################################################################
            # en_US: Creates a page drawing object for each label.
            # page = Drawing(label_width_mm*mm, label_height_mm*mm)
            # frappe.msgprint(_("Success19.3A"))

            # Print the flyer elements
            copies_per_element = 10
            
            # Offset the text elements by the width of the QR code
            qr_code_width = 75
            qr_code_height = -5

            for idx in range(copies_per_element):
              for element in this_label_format["elements"]:
                  # en_US: We check which type of element we need to draw
                  if element["element_type"] == "wrapper-section":
                      # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                      PDFcanvas.setFont(element["font_name"], 20)
                      #PDFcanvas.roundRect(x=100, y=110, width=50, height=50, radius=5, stroke=1, fill=1, style='Blue')   
                      PDFcanvas.roundRect(0, 5, 25, 50, 50, stroke=1, fill=1, style='Blue')

                      # Declare a drawing with size to act as a bg div
                      # d = Drawing(label_width_mm*mm, label_height_mm*mm)

                      # set drawing color (background???)
                      # d.setFillColorRGB(txt_red,txt_grn,txt_blu)

                      # Add previously created elements
                      # d.add(barcode_eanbc13)

                      # d.add(my_qr_code)

                      # Render it onto the PDF:
                      # args:
                      # 1 the drawing object
                      # 2. the canvas where we want to render our object
                      # 3. xpos
                      # 4. ypos

                      # renderPDF.draw(d, PDFcanvas, 0, 0)


                  elif element["element_type"] == "receipt_date":
                      # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                      xpos = element["x_pos_mm"]*mm + qr_code_width
                      ypos = element["y_pos_mm"]*mm + qr_code_height
                      PDFcanvas.setFont(element["font_name"], 12)
                      receipt_date_txt = "Origin Packed Date: " + receipt_date
                      PDFcanvas.drawString(xpos, ypos, receipt_date_txt)
                  elif element["element_type"] == "item_name":
                      # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                      xpos = element["x_pos_mm"]*mm + qr_code_width
                      ypos = element["y_pos_mm"]*mm + qr_code_height
                      PDFcanvas.setFont('Helvetica', 12)
                      PDFcanvas.drawString(xpos, ypos, tunart_url)
                  elif element["element_type"] == "serial_no":
                      # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                      xpos = element["x_pos_mm"]*mm + qr_code_width
                      ypos = element["y_pos_mm"]*mm + qr_code_height
                      PDFcanvas.setFont('Helvetica', 12)
                      serial_no_txt = each_label_object["serial_no"]
                      PDFcanvas.drawString(xpos, ypos, serial_no_txt)
                  elif element["element_type"] == "paragraph":
                      ###############################################################################
                      #
                      #   13.4.? Add the Product description as a paragraph
                      #
                      ###############################################################################
                      prod_x_pos += qr_code_width
                      prod_y_pos += qr_code_height
                      frappe.msgprint(_("Success-ISTEXT"))
                      label_prod_desc_area = Paragraph(curr_tuple_label_desc, style=label_styles["Blue"])
                      label_prod_desc_area.wrapOn(PDFcanvas, prod_x_wrap, prod_y_wrap)
                      label_prod_desc_area.drawOn(PDFcanvas, prod_x_pos, prod_y_pos, mm)

                      ###############################################################################
                      #
                      #   13.4.? Add line 3 (below Prod description 1 or 2 lines) as a paragraph
                      #
                      ###############################################################################

                      # No Mostrara las fechas
                      if sticker_type == '0':
                          pass

                      # Mostrara unicamente la fecha de cosecha
                      if sticker_type == '1':
                          label_line3_area = Paragraph(line_3_text, style=styles["line3"])
                          label_line3_area.wrapOn(PDFcanvas, line_3_x_wrap, line_3_y_wrap)
                          label_line3_area.drawOn(PDFcanvas, line_3_x_pos, line_3_y_pos, mm)

                      # Mostrara unicamente la fecha de vencimiento
                      if sticker_type == '2':
                          label_line4_area = Paragraph(line_4_text, style=styles["line4"])
                          label_line4_area.wrapOn(PDFcanvas, line_4_x_wrap, line_4_y_wrap)
                          label_line4_area.drawOn(PDFcanvas, line_4_x_pos, line_4_y_pos, mm)

                      if sticker_type == '3':
                          label_line3_area = Paragraph(line_3_text, style=styles["line3"])
                          label_line3_area.wrapOn(PDFcanvas, line_3_x_wrap, line_3_y_wrap)
                          label_line3_area.drawOn(PDFcanvas, line_3_x_pos, line_3_y_pos, mm)

                          label_line4_area = Paragraph(line_4_text, style=styles["line4"])
                          label_line4_area.wrapOn(PDFcanvas, line_4_x_wrap, line_4_y_wrap)
                          label_line4_area.drawOn(PDFcanvas, line_4_x_pos, line_4_y_pos, mm)

                      #PDFcanvas.setFont('vera', 32)
                      #This draws the text strings, gets position numbers from variables at beggining of file.

                      """ OPTIONAL IF YOU REGISTER A BARCODE FONT, THIS IS ANOTHER WAY TO SET IT UP
                      barcode_string = '<font name="Free 3 of 9 Regular" size="12">%s</font>'
                          barcode_string = barcode_string % "1234567890"
                      """
                      #line_1_and_2 = '<font name="Helvetica" size="12">%s</font>'
                      #line_1_and_2 = line_1_and_2 % line_1_txt

                  elif element["element_type"] == "ean13barcode":
                      # 7.4 Defining the quiet space value
                      #if barcode_use_quiet_space == 'yes':
                      #    quiet_space = 'TRUE'

                      ###############################################################################
                      #
                      #   19.2.1 Obtain the contents of the unique label list tuples
                      #
                      ###############################################################################
                      curr_tuple_label_desc = str(each_label_tuple[0])
                      curr_tuple_label_barcode = str(each_label_tuple[1])
                      #print("Current Code from tuple: " + curr_tuple_label_barcode)
                      #print("Current Product from tuple: " + curr_tuple_label_desc)

                      ###############################################################################
                      #
                      #   19.2.2 Draw the EAN-13 Code
                      #
                      ###############################################################################
                      # Pass barcode creation parameters to reportlab, any order, as name=value pairs.
                      # Order may be changed, since reportlab maps name=value pairs automatically.
                      # Source code for ordering
                      # http://pydoc.net/Python/reportlab/3.3.0/reportlab.graphics.barcode.eanbc/

                      barcode_eanbc13 = eanbc.Ean13BarcodeWidget(value=curr_tuple_label_barcode,fontName=element["fontName"],fontSize=element["fontSize"],x=element["x_pos_mm"]*mm,y=element["y_pos_mm"]*mm,barFillColor=bar_fill_color,barHeight=element["barHeight"],barWidth=element["barWidth"],barStrokeWidth=element["barStrokeWidth"],barStrokeColor=bar_stroke_color,textColor=barcode_text_color,humanReadable=element["humanReadable"],quiet=element["quiet"],lquiet=element["lquiet"],rquiet=element["rquiet"])

                      ###############################################################################
                      #
                      #   13.4.? Add the barcode and position it on the PDFcanvas
                      #
                      ###############################################################################
                      page.add(barcode_eanbc13)
                      # Place the generated barcode on the page.
                      # (Drawing object, Barcode object, x position, y position)
                      renderPDF.draw(page, PDFcanvas, 0, 0)

                  elif element["element_type"] == "logo_image" and image_logo_filename != "not found":
                      try:
                          PDFcanvas.drawImage(image_logo_filename, int(element["x_pos_px"]), int(element["y_pos_px"]), width=None,height=int(element["height_px"]),mask=None,preserveAspectRatio=True)
                          # PDFcanvas.drawImage(image_logo_filename, element["x_pos_mm"]*mm, element["y_pos_mm"]*mm, width=None, height='30', mask=None, preserveAspectRatio=True,  anchor='c')
                      except:
                          frappe.msgprint(_("Could not draw image")+str(frappe.get_traceback()))
                          """
                          elif element["element_type"] == "qrcode":
                              # draw qrcode
                          """

                                  # Draw the QR code with the web page
                  elif element["element_type"] == "qr_code":
                    try:
                      # en_US: If one of the elements has text, then you add it to the PDF Canvas.
                      PDFcanvas.setFont('Helvetica', 20)
                      
                      # We create a list with possible content options for the QR code. Will help with quick changes during first production run.
                      qr_contents = ('https://www.tunart.com/','https://tunart.biz','https://tunart.biz/tracemyfish/')
                      
                      # en_US: We specify the position of the QR code element in mm from the left and bottom of page.
                      # en_US: We also provide a percentage scale for quick and easy adjustment when draing on the page. Default = 100.0  Larger numbers will enlarge the QR.

                      scaling_percent = 40.0
                      unit = 100.0
                      # en_US:  First, we draw a QR code with the selected contents. For now it is a URL. Plan is to call a webpage which calls a Python method delivering data for that specific shipment.
                      qr_code = qr.QrCodeWidget(qr_contents[0])
                      # en_US: We get the bounds of the drawn QR Code. This will help resize.
                      bounds = qr_code.getBounds() # Returns position x, position y, size x, size y
                      # en_US: We set the width of the QR code drawing to the width bounds returned
                      width = bounds[2] - bounds[0]
                      # en_US: We set the width of the QR code drawing to the width bounds returned
                      height = bounds[3] - bounds[1]
                      # en_US: We create a drawing container with a specified size. We adjust the container to fit the QR Code, using the object size and a percentage amount
                      d = Drawing(unit, unit, transform=[(scaling_percent/width)*mm,0,0,(scaling_percent/height)*mm,0,0])
                                        
                      # en_US: We add the QR code to the code container
                      d.add(qr_code)
                      # en_US: We draw contents of d container with QR Code, on canvas c, at x position, y position
                      qr_code_x_pos_mm = 2
                      qr_code_y_pos_mm = 26
                      renderPDF.draw(d, PDFcanvas, qr_code_x_pos_mm*mm, qr_code_y_pos_mm*mm)
                      #c.drawImage(image, 10, 10, width=None,height=None,mask=None)

                    except:
                      frappe.msgprint("Could not draw QR code " + frappe.get_traceback())

              # For every Label Item, we must show the page.
              PDFcanvas.showPage()
        
        # frappe.msgprint(_("Before if"))
        if os.path.exists(server_file_path):
            PDFcanvas.save()
        else:
            # This portion creates the folder where the sticker file will be saved to.
            frappe.create_folder(server_file_path)
            # This portion creates the folder and saves it to the sites directory specified.
            PDFcanvas.save()

        # en_US:  We want to return the URL of the file directly for download in ERPNext.
        file_url = f'files/pdflabels/{date_time_fileName_PDF_w_ext}'

        # return file_url
        return file_url

    except:
        # exception_message = _("Label configuration script could not be loaded. Please check ") + label_config_file
        exception_message = _("Label creation failed")
        frappe.msgprint(exception_message, traceback.format_exc())

        return exception_message