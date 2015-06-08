__author__ = 'mlaird'
import default_app_db
from general_html_functions import *


def main_page():
    output = ["<h3>Main Page</h3>"]
    for t in default_app_db.db_tables:
        output.append("<p><a href='/%s'>%s Management Page</a></p>" % (t, default_app_db.db_tables[t]['label']))

    return output


def table_management_page(table_name, form_data=None):
    if form_data:
        add_res = default_app_db.add_table_row(table_name, form_data)
    else:
        add_res = False
    output = ["<h3>%s Management</h3>" % default_app_db.db_tables[table_name]['label'], "<p><b>Known entries:</b></p>"]
    entries = default_app_db.get_all_table_rows(table_name)
    if len(entries) > 0:
        entries_table = make_html_table_from_db_table(default_app_db.db_tables[table_name], entries, 'dbTable')
        output.extend(entries_table.return_table())
        output.extend("<p><a href='/%s/edit'>Edit these entries.</a></p>" % table_name)
    else:
        output.append("<p>There are no entries in the database.</p>")

    if form_data:
        if add_res:
            output.append("<p>New entry added!</p>")
        else:
            output.append("<p>New entry could not be added to the database.</p>")

    new_entry_form = make_html_form_from_db_table_dict(default_app_db.db_tables[table_name],
                                                       default_app_db.get_joined_table_rows(table_name))

    new_entry_form.set_title('Add new entry:')

    output.extend(new_entry_form.return_form())

    output.append("<p><a href='/'>Return to the main page.</a></p>")
    output.append("<script type='text/javascript'>document.onload = "
                  "setTableHeaderClickFunctions('dbTable','headerRow');</script>")
    return output


def list_rows_for_editing_page(table_name):
    output = ["<h3>Edit %s</h3>" % default_app_db.db_tables[table_name]['label'], "<p><b>Known entries:</b></p>"]

    entries = default_app_db.get_all_table_rows(table_name)

    if len(entries) > 0:
        entries_table = HtmlTable()
        for e in entries:
            row_to_add = []
            id_string = ""
            for uc in default_app_db.db_tables[table_name]['unique_columns']:
                id_string += "%s " % e[uc]
            row_to_add.append(id_string)
            edit_form = HtmlForm()
            delete_form = HtmlForm()
            edit_form.open_form = "<form method='post' action='/%s/edit'>" % table_name
            delete_form.open_form = "<form method='post' action='/%s/delete'>" % table_name
            for c in default_app_db.db_tables[table_name]['columns']:
                edit_form.add_hidden_input(c['name'], e[c['name']])
                delete_form.add_hidden_input(c['name'], e[c['name']])
            edit_form.add_submit_button('Edit')
            delete_form.add_submit_button('Delete')
            row_to_add.append(''.join(edit_form.return_form()))
            row_to_add.append(''.join(delete_form.return_form()))
            entries_table.add_row(row_to_add)
        output.extend(entries_table.return_table())

    output.append("<p><a href='/'>Return to the main page.</a></p>")

    return output


def edit_db_row_page(table_name, form_data):
    output = ["<h3>Edit %s</h3>" % default_app_db.db_tables[table_name]['label']]
    if 'confirm_edit' in form_data.keys():
        if default_app_db.update_table_row(table_name, form_data):
            output.append('<p>Database entry updated.</p>')
        else:
            output.append('<p>Database entry could not be updated.</p>')
    edit_entry_form = make_html_form_from_db_table_dict(default_app_db.db_tables[table_name],
                                                        default_app_db.get_joined_table_rows(table_name),
                                                        form_data)
    edit_entry_form.add_hidden_input('confirm_edit', True)
    for col_name in form_data.keys():
        if '_old_' != col_name[5:]:
            edit_entry_form.add_hidden_input('_old_' + col_name, form_data[col_name])
    output.extend(edit_entry_form.return_form())
    output.append("<p><a href='/'>Return to the main page.</a></p>")

    return output


def delete_db_row_page(table_name, form_data):
    output = ["<h3>Delete Entry</h3>"]
    if 'confirm_delete' in form_data.keys():
        if default_app_db.delete_table_row(table_name, form_data):
            output.append("<p>Database entry deleted.</p>")
        else:
            output.append("<p>Database entry could not be deleted.</p>")
    else:
        id_string = ""
        for uc in default_app_db.db_tables[table_name]['unique_columns']:
            id_string += "%s " % form_data[uc]
        output.append("<p>You are going to delete the entry '%s' from the '%s' table.</p>" %
                      (id_string, default_app_db.db_tables[table_name]['label']))
        confirm_delete_form = HtmlForm()
        confirm_delete_form.add_text_line('<b>Are you sure?</b>')
        confirm_delete_form.add_submit_button('Delete')
        confirm_delete_form.add_hidden_input('confirm_delete', True)
        for col_name in form_data.keys():
            confirm_delete_form.add_hidden_input(col_name, form_data[col_name])
        output.extend(confirm_delete_form.return_form())
    output.append("<p><a href='/'>Return to the main page.</a></p>")

    return output

def not_found_error_page():
    output = ["<p>This page could not be found.</p>"]

    return output
