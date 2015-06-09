__author__ = 'mtk-user'

# import general_sqlite_db_functions
import copy


class HtmlForm():
    def __init__(self):
        self.html = []
        self.open_form = "<form method='post'>"
        self.close_form = "</form>"
        self.title = ''
        self.target = ''

    def add_text_input(self, prompt, name, value='', element_id=''):
        if element_id != '':
            self.html.append("<p>%s: <input type=text name='%s' value='%s' id='%s'></p>" %
                             (prompt, name, value, element_id))
        else:
            self.html.append("<p>%s: <input type=text name='%s' value='%s'></p>" % (prompt, name, value))

    def add_text_line(self, text):
        self.html.append("<p>%s</p>" % text)

    def add_textarea_input(self, prompt, name, value=''):
        self.html.append("<p>%s: <textarea name='%s'>%s</textarea></p>" % (prompt, name, value))

    def add_hidden_input(self, name, value, element_id=''):
        if element_id != '':
            self.html.append("<input type=hidden name='%s' value='%s' id='%s'>" % (name, value, element_id))
        else:
            self.html.append("<input type=hidden name='%s' value='%s'>" % (name, value))

    def add_select_dropdown(self, prompt, name, options, option_value_name, option_text_name, set_value=None):
        self.html.append("<p>%s: <select name=%s>" % (prompt, name))
        for option in options:
            if str(set_value) == str(option[option_value_name]):
                self.html.append("<option value='%s' selected>%s</option>" % (option[option_value_name],
                                                                              option[option_text_name]))
            else:
                self.html.append("<option value='%s'>%s</option>" % (option[option_value_name],
                                                                     option[option_text_name]))
        self.html.append("</select></p>")

    def add_submit_button(self, value='Submit'):
        self.html.append("<p><input type=submit value='%s'></p>" % value)

    def set_title(self, form_title):
        self.title = form_title

    def print_form(self):
        full_html = [self.open_form]
        if self.title:
            full_html.append("<p><b>%s</b></p>" % self.title)
        full_html.extend(self.html)
        full_html.append(self.close_form)
        for line in full_html:
            print line

    def return_form(self):
        full_html = [self.open_form]
        if self.title:
            full_html.append("<p><b>%s</b></p>" % self.title)
        full_html.extend(self.html)
        full_html.append(self.close_form)
        return full_html


class HtmlTable():
    table_class_default = "<table>"

    def __init__(self, columns=None, table_id=None):
        self.body_rows = []
        self.header = []
        if columns is None:
            self.columns = []
        else:
            self.columns = columns
        self.make_header(self.columns)
        self.table_class = self.table_class_default
        self.close_table = "</table>"
        self.table_id = table_id

    def make_header(self, columns):
        if len(columns) > 0:
            header_html = "<thead><tr id=headerRow>"
            for c in columns:
                header_html += "<th id='%s'>%s</th>" % (c['desc'].replace(' ', '_'), c['desc'])
            header_html += "</tr></thead>"
        else:
            header_html = ""
        self.header = header_html

    def add_row(self, data):
        row_html = "<tr>"
        if type(data) is list:
            for d in data:
                row_html += "<td>%s</td>" % d
        elif type(data) is dict:
            for c in self.columns:
                row_html += "<td>%s</td>" % data[c['name']]
        row_html += "</tr>"
        self.body_rows.append(row_html)

    def add_multiple_rows(self, dataset):
        for d in dataset:
            self.add_row(d)

    def return_table(self):
        open_table = "<table"
        if self.table_class:
            open_table += " class='%s'" % self.table_class
        if self.table_id:
            open_table += " id='%s'" % self.table_id
        open_table += ">"
        full_html = [open_table, self.header, "<tbody>"]
        full_html.extend(self.body_rows)
        full_html.append("</tbody>")
        full_html.append(self.close_table)
        return full_html


class DocumentReadyFunction():
    def __init__(self):
        self.script = []
        self.open_script = "<script type='text/javascript'> $(document).ready(function() {\n"
        self.close_script = "});</script>"

    def add_autocomplete_function(self, variable_name, get_values_function, ac_input_id, value_input_id, item_id):
        self.script.append("var %s = %s;\n" % (variable_name, get_values_function))
        self.script.append("$('%s').autocomplete({\n" % ac_input_id)
        self.script.append("source: %s,\n" % variable_name)
        self.script.append("select: function(evt, ui){\n")
        self.script.append("$('%s').val(ui.item.%s); } });\n" % (value_input_id, item_id))

    def return_script(self):
        full_script = [self.open_script]
        full_script.extend(self.script)
        full_script.append(self.close_script)
        return full_script


class WebResponse:
    def __init__(self, params):
        self.head = []
        self.body = []
        self.content_type = 'html'
        self.status = '200 OK'
        self.headers = []
        self.response = []
        if 'html_wrapper_open' in params:
            self.html_wrapper_open = self._listify(params['html_wrapper_open'])
        else:
            self.html_wrapper_open = []
        if 'html_wrapper_close' in params:
            self.html_wrapper_close = self._listify(params['html_wrapper_close'])
        else:
            self.html_wrapper_close = params['html_wrapper_close']
        if 'bootstrap' in params:
            self.add_head([
                '<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">'
                '<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>'
                '<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>'])

    @staticmethod
    def _listify(content):
        if type(content) == list:
            return content
        elif type(content) == str:
            return [content]
        else:
            return []

    def set_status(self, given_return_status):
        status_list = {'OK': '200 OK', 'Not Found': '404 Not Found', 'Forbidden': '403 Forbidden',
                       'Server Error': '500 Internal Server Error'}
        if given_return_status in status_list:
            self.status = status_list[given_return_status]
        else:
            self.status = status_list['Server Error']

    def set_content_type(self, given_content_type):
        content_type_list = ['html', 'json', 'xml', 'css', 'javascript']
        if given_content_type in content_type_list:
            self.content_type = given_content_type

    def make_response(self):
        if self.content_type == 'html':
            output = ['<html>']
            if self.head:
                output.append('<head>')
                output.extend(self.head)
                output.append('</head>')
        else:
            output = []
        if self.body:
            if self.content_type == 'html':
                output.append('<body>')
                output.extend(self.html_wrapper_open)
            output.extend(self.body)
            if self.content_type == 'html':
                output.extend(self.html_wrapper_close)
                output.append('</body>')
        if self.content_type == 'html':
            output.append('</html>')
        self.response = output

    def make_headers(self):
        self.make_response()
        if self.content_type in ['javascript', ]:
            media_type = 'application'
        else:
            media_type = 'text'
        headers = [('Content-type', '%s/%s' % (media_type, self.content_type)),
                   ('Content-Length', '%s' % self.get_response_length())]
        self.headers = headers

    def get_response_length(self):
        return sum(len(line) for line in self.response)

    def add_body(self, body_text):
        self.body.extend(self._listify(body_text))

    def add_head(self, head_text):
        self.head.extend(self._listify(head_text))


def make_html_form_from_db_table_dict(db_dict, joined_table_rows=None, set_values=None):
    form = HtmlForm()
    for c in db_dict['columns']:
        form_element_added = False
        if db_dict['joined_tables']:
            for jt in db_dict['joined_tables']:
                if c['name'] == jt['column']:
                    if set_values:
                        form.add_select_dropdown(c['desc'], c['name'], joined_table_rows[jt['table']], c['name'],
                                                 jt['label'], set_values[c['name']])
                    else:
                        form.add_select_dropdown(c['desc'], c['name'], joined_table_rows[jt['table']], c['name'],
                                                 jt['label'])
                    form_element_added = True
        if not form_element_added:
            if c['type'] in ['INTEGER', 'TEXT', 'DATE']:
                if set_values:
                    form.add_text_input(c['desc'], c['name'], set_values[c['name']])
                else:
                    form.add_text_input(c['desc'], c['name'])
    form.add_submit_button()
    return form


def make_html_table_from_db_table(db_dict, rows, table_id=None):
    if db_dict['index_column']:
        no_index_cols = copy.deepcopy([x for x in db_dict['columns'] if x['name'] not in db_dict['index_column']])
    else:
        no_index_cols = copy.deepcopy(db_dict['columns'])

    if db_dict['joined_tables']:
        for c in no_index_cols:
            for jt in db_dict['joined_tables']:
                if c['name'] == jt['column']:
                    c['name'] = jt['label']
    table = HtmlTable(no_index_cols, table_id)
    table.add_multiple_rows(rows)
    return table