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

        // frm.add_custom_button(__('Download'), function () {
        //     var file_url = frm.doc.file_url;
        //     if (frm.doc.file_name) {
        //         file_url = file_url.replace(/#/g, '%23');
        //     }
        //     window.open(file_url);
        // }, "fa fa-download");
    }
});
