frappe.ui.form.on("Production Plan", {
    refresh: function (frm) {

        // Agrega un icon-button a la barra de la pagina
        cur_frm.page.add_action_icon(__("fa fa-file-pdf-o"), function () {

            // Instanciando un dialogo con sus propiedades
            let dialog = new frappe.ui.Dialog({
                title: __('Generar Stickers'),
                fields: [
                    {
                        fieldtype: 'Select',
                        fieldname: 'sticker_type',
                        label: __('Estilo de sticker'),
                        reqd: true,
                        options: [
                            "Sticker sin fechas",
                            "Sticker con fecha de cosecha",
                            "Sticker con fecha de vencimiento",
                            "Sticker con todos los datos"
                        ],
                        description: __('Seleccione el estilo de sticker que desee generar')
                    },
                    {
                        fieldtype: 'Button',
                        fieldname: 'btn_generar',
                        label: __('Generar Stickers'),
                        options: '',
                        description: __(''),
                    }
                ]
            });

            // Muestra el dialogo
            dialog.show();

            // Agrega un event lister al boton del dialogo
            dialog.fields_dict.btn_generar.$wrapper.on('click', function (e) {
                var estilo_sticker = '0';

                if (dialog.fields_dict.sticker_type.value == 'Sticker sin fechas') {
                    estilo_sticker = '0';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con fecha de cosecha') {
                    estilo_sticker = '1';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con fecha de vencimiento') {
                    estilo_sticker = '2';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con todos los datos') {
                    estilo_sticker = '3';
                }

                // Frappe call that simply opens a google page in a new tab or window  (for debugging API methods.)
                /*
                frappe.call({
                    method: "labels.api_labels2.test_method",
                    args: {
                        sticker_type: estilo_sticker
                    },
                    callback: function (r) {
                        // El valor retornado, es la url de la ubicacion del archivo
                        window.open(r.message);
                    }
                });
                */
                frappe.call({
                    method: "labels.api_labels.process_labels",
                    args: {
                        dict_data: cur_frm.doc.po_items,
                        sticker_type: estilo_sticker,
                        production_date: cur_frm.doc.label_production_date,
                        expiration_date: cur_frm.doc.label_expiration_date
                    },
                    callback: function (r) {
                        // El valor retornado, es la url de la ubicacion del archivo
                        window.open(r.message);
                    }
                });
            });
        });
    }
});

frappe.ui.form.on("Purchase Receipt", {
    refresh: function (frm) {

        // Agrega un icon-button a la barra de la pagina
        cur_frm.page.add_action_icon(__("fa fa-file-pdf-o"), function () {

            // Instanciando un dialogo con sus propiedades
            let dialog = new frappe.ui.Dialog({
                title: __('Create Labels'),
                fields: [
                    {
                        fieldtype: 'Select',
                        fieldname: 'sticker_type',
                        label: __('Label Style'),
                        reqd: true,
                        options: [
                            "Ingreso 105mm x 155mm"
                            /*
                            "Sticker con fecha de cosecha",
                            "Sticker con fecha de vencimiento",
                            "Sticker con todos los datos"
                            */
                        ],
                        description: __('Please select the label style you wish to create')
                    },
                    {
                        fieldtype: 'Button',
                        fieldname: 'btn_generar',
                        label: __('Create Labels'),
                        options: '',
                        description: __(''),
                    }
                ]
            });

            // Muestra el dialogo
            dialog.show();

            // Agrega un event lister al boton del dialogo
            dialog.fields_dict.btn_generar.$wrapper.on('click', function (e) {
                var sticker_style = '0';

                if (dialog.fields_dict.sticker_type.value == 'Ingreso 105mm x 155mm') {
                    sticker_style = 'incoming_serial_no105x155';
                }
                /*
                if (dialog.fields_dict.sticker_type.value == 'Sticker con fecha de cosecha') {
                    estilo_sticker = '1';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con fecha de vencimiento') {
                    estilo_sticker = '2';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con todos los datos') {
                    estilo_sticker = '3';
                }
                */

                // Frappe call that simply opens a google page in a new tab or window  (for debugging API methods.)
                /*
                frappe.call({
                    method: "labels.api_labels2.test_method",
                    args: {
                        sticker_type: estilo_sticker
                    },
                    callback: function (r) {
                        // El valor retornado, es la url de la ubicacion del archivo
                        window.open(r.message);
                    }
                });
                */
                frappe.call({
                method: "labels.api_labels.purchase_receipt_labels",
                args: {

                    /*
                    dict_data: cur_frm.doc.items,
                    sticker_type: estilo_sticker,
                    production_date: cur_frm.doc.label_production_date,
                    expiration_date: cur_frm.doc.label_expiration_date
                    */
                    // Dummy Data
                    /*
                    dict_data: [
                        {
                            "item_name": "Atun de compra",
                            "serial_no": "YFT2020-07-13-02398"
                        },
                        {
                            "item_name": "Atun de compra",
                            "serial_no": "YFT2020-07-13-01685"
                        }
                    ],
                    */
                    dict_data: cur_frm.doc.items,
                    label_format: sticker_style,
                    receipt_date: "13-07-2020"
                    
                },
                callback: function (r) {
                    // We show an alert that the stickers have been generated
                    frappe.show_alert({
                        indicator: 'orange',
                        message: r.message
                    });
                    window.open(r.message);
                }
                });
            });
        });
    }
});

frappe.ui.form.on("Delivery Note", {
    refresh: function (frm) {

        // en_US: Adds an icon-button near the action buttons on the framework.
        // es: Agrega un boton / icono al lado de los botones de accion del marco frappe.
        cur_frm.page.add_action_icon(__("fa fa-file-pdf-o"), function () {

            // en_US: We instantiate a dialog with its properties.
            // es: Instanciamos el dialogo con sus propiedades.
            let dialog = new frappe.ui.Dialog({
                title: __('Create Labels'),
                fields: [
                    {
                        fieldtype: 'Select',
                        fieldname: 'sticker_type',
                        label: __('Label Style'),
                        reqd: true,
                        options: [
                            "Ingreso 105mm x 155mm",
                            "105mmx155mm Serial No and EAN-13 Barcode"
                        ],
                        description: __('Please select the label style you wish to create')
                    },
                    {
                        fieldtype: 'Button',
                        fieldname: 'btn_generar',
                        label: __('Create Labels'),
                        options: '',
                        description: __(''),
                    }
                ]
            });

            // en_US: We show the dialog.
            // es: Mostramos el diálogo.
            dialog.show();

            // en_US: Adds an event listenet below the dialog
            // es: Agrega un event lister al boton del dialogo
            dialog.fields_dict.btn_generar.$wrapper.on('click', function (e) {
                var sticker_style = '0';

                // en_US: Options in the dialog assign a value to the sticker format to be called on the back end.
                // es: Opciones en el dialogo le asignan un valor al formato de etiqueta para ser llamado en el servidor.
                if (dialog.fields_dict.sticker_type.value == 'Empaque 105mm x 155mm') {
                    sticker_style = 'outgoing_serial_no_plus_barcode';
                }
                
                if (dialog.fields_dict.sticker_type.value == 'Product Flyers 10 per serial') {
                    sticker_style = '1';
                }
                /*
                if (dialog.fields_dict.sticker_type.value == 'Sticker con fecha de vencimiento') {
                    estilo_sticker = '2';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con todos los datos') {
                    estilo_sticker = '3';
                }
                */

                // Frappe call that simply opens a google page in a new tab or window  (for debugging API methods.)
                /*
                frappe.call({
                    method: "labels.api_labels2.test_method",
                    args: {
                        sticker_type: estilo_sticker
                    },
                    callback: function (r) {
                        // El valor retornado, es la url de la ubicacion del archivo
                        window.open(r.message);
                    }
                });
                */
                frappe.call({
                method: "labels.api_labels.delivery_note_labels",
                args: {
                    /*
                    dict_data: cur_frm.doc.po_items,
                    sticker_type: estilo_sticker,
                    production_date: cur_frm.doc.label_production_date,
                    expiration_date: cur_frm.doc.label_expiration_date
                    */
                   // Dummy Data
                    dict_data: cur_frm.doc.items,
                    label_format: sticker_style,
                    receipt_date: "13-07-2020"
                },
                callback: function (r) {
                    // We show an alert that the stickers have been generated
                    frappe.show_alert({
                        indicator: 'orange',
                        message: r.message
                    });
                }
                });
            });
        });
    }
});

frappe.ui.form.on("Stock Entry", {
    refresh: function (frm) {

        // Agrega un icon-button a la barra de la pagina
        cur_frm.page.add_action_icon(__("fa fa-file-pdf-o"), function () {

            // Instanciando un dialogo con sus propiedades
            let dialog = new frappe.ui.Dialog({
                title: __('Create Labels'),
                fields: [
                    {
                        fieldtype: 'Select',
                        fieldname: 'sticker_type',
                        label: __('Label Style'),
                        reqd: true,
                        options: [
                            "Sticker sin fechas",
                            "105mmx155mm Serial No and EAN-13 Barcode"
                        ],
                        description: __('Seleccione el estilo de sticker que desee generar')
                    },
                    {
                        fieldtype: 'Button',
                        fieldname: 'btn_generar',
                        label: __('Create Labels'),
                        options: '',
                        description: __(''),
                    }
                ]
            });

            // Muestra el dialogo
            dialog.show();

            // Agrega un event lister al boton del dialogo
            dialog.fields_dict.btn_generar.$wrapper.on('click', function (e) {
                var estilo_sticker = '0';

                if (dialog.fields_dict.sticker_type.value == 'Sticker sin fechas') {
                    estilo_sticker = '0';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con fecha de cosecha') {
                    estilo_sticker = '1';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con fecha de vencimiento') {
                    estilo_sticker = '2';
                }
                if (dialog.fields_dict.sticker_type.value == 'Sticker con todos los datos') {
                    estilo_sticker = '3';
                }

                // Frappe call that simply opens a google page in a new tab or window  (for debugging API methods.)
                /*
                frappe.call({
                    method: "labels.api_labels2.test_method",
                    args: {
                        sticker_type: estilo_sticker
                    },
                    callback: function (r) {
                        // El valor retornado, es la url de la ubicacion del archivo
                        window.open(r.message);
                    }
                });
                */
                frappe.call({
                    method: "labels.api_labels.process_labels_2",
                    args: {
                        /*
                        dict_data: cur_frm.doc.po_items,
                        sticker_type: estilo_sticker,
                        production_date: cur_frm.doc.label_production_date,
                        expiration_date: cur_frm.doc.label_expiration_date
                        */
                       // Dummy Data
                       dict_data: 1,
                       sticker_type: 1,
                       production_date: 1,
                       expiration_date: 1
                    },
                    callback: function (r) {
                        // We show an alert that the stickers have been generated
                        frappe.show_alert({
                            indicator: 'orange',
                            message: r.message
                        });
                    }
                });
            });
        });
    }
});

console.log("'Labels' has been loaded.");
