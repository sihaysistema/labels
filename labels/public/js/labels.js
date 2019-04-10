frappe.ui.form.on("Production Plan", {
    refresh: function (frm) {
        frm.add_custom_button(__('GENERAR ETIQUETA'), function () {
            frappe.call({
                method: "labels.api_labels.child_table_to_csv",
                args: {
                    dict_data: cur_frm.doc.mr_items
                },
                callback: function () {
                    // frm.reload_doc();
                }
            });
        }).addClass("btn-primary");
    }
});

// frappe.ui.form.on("Production Plan", {
//     onload: function (frm) {
//         let btn = document.createElement('a');
//         btn.innerText = 'Refresh';
//         btn.className = 'grid-upload btn btn-xs btn-default';
//         frm.fields_dict.items.grid.wrapper.find('.grid-upload').removeClass('hide').parent().append(btn);
//         btn.addEventListener("click", function () {
//         });
//     }
// })