frappe.ui.form.on("Production Plan", {
    refresh: function (frm, cdt, cdn) {
        frm.add_custom_button(__('GENERAR ETIQUETA'), function () {
            // frappe.call({
            //     method: "factura_electronica.api.guardar_pdf_servidor",
            //     args: {
            //         nombre_archivo: frm.doc.name,
            //         cae_de_factura_electronica: frm.doc.cae_factura_electronica
            //     },
            //     callback: function () {
            //         frm.reload_doc();
            //     }
            // });
        }).addClass("btn-primary");
    }
});