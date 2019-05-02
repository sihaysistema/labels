frappe.ui.form.on("Production Plan", {
    refresh: function (frm) {
        frm.add_custom_button(__('GENERAR ETIQUETA'), function () {
            frappe.call({
                method: "labels.api_labels.child_table_to_csv",
                args: {
                    dict_data: cur_frm.doc.po_items
                },
                callback: function (r) {
                    window.open(r.message);
                }
            });
        }).addClass("btn-primary");

        frm.add_custom_button(__('GENERAR STICKER'), function () {
            frappe.call({
                method: "jsonshare.utils.obtener_usuarios",
                callback: function (response) {
                    // Crea un Modal(dialogo), en las opciones del campo
                    // user_share se asigna el listado de usarios retornados
                    let dialog = new frappe.ui.Dialog({
                        title: __('Compartir Item'),
                        fields: [
                            {
                                fieldtype: 'Select',
                                fieldname: 'user_share',
                                label: __('Seleccione Usuario'),
                                reqd: true,
                                options: response.message,
                                description: __('Seleccione el host/usuario con quien quiera compartir el Item')
                            },
                            {
                                fieldtype: 'Button',
                                fieldname: 'btn_share',
                                label: __('Compartir'),
                                options: '',
                                description: __(''),
                            }
                        ]
                    });

                    // Muestra el dialogo
                    dialog.show();

                    // Agrega un event lister al boton compartir del dialogo
                    dialog.fields_dict.btn_share.$wrapper.on('click', function (e) {
                        console.log(dialog.fields_dict.user_share.value);
                        frappe.call({
                            method: "jsonshare.api.crud",
                            args: {
                                item: codigo,
                                usuario: dialog.fields_dict.user_share.value,
                                doctype: doctype
                            },
                            callback: function () {
                                // frm.reload_doc();
                            }
                        });
                    });
                }
            });

        }).addClass("btn-success");

        cur_frm.page.add_action_icon(__("fa fa-sticky-note"), function () {

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
                            "Sticker con fecha de vencimiento"
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

            // Agrega un event lister al boton compartir del dialogo
            dialog.fields_dict.btn_generar.$wrapper.on('click', function (e) {
                console.log(dialog.fields_dict.sticker_type.value);
                // frappe.call({
                //     method: "jsonshare.api.crud",
                //     args: {
                //         item: codigo,
                //         usuario: dialog.fields_dict.user_share.value,
                //         doctype: doctype
                //     },
                //     callback: function () {
                //         // frm.reload_doc();
                //     }
                // });
            });
        });
    }
});
