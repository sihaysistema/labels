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

                // console.log(estilo_sticker);

                frappe.call({
                    method: "labels.api_labels.child_table_to_csv",
                    args: {
                        dict_data: cur_frm.doc.po_items,
                        sticker_type: estilo_sticker
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
