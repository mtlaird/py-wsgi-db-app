__author__ = 'mlaird'

from wsgiref.simple_server import make_server
from pprint import pformat
import urlparse
import default_web
from general_sqlite_db_functions import db_tables, check_schema


def get_form_data(wsgi_input, content_length):
    form_data = pformat(wsgi_input.read(content_length))
    form_data = form_data.replace("'", "")
    form_data = urlparse.parse_qs(form_data)
    for d in form_data:
        if type(form_data[d]) is list:
            form_data[d] = form_data[d][0]
    return form_data


def application(environ, start_response):

    response_params = {'html_wrapper_open': '<div class=container>',
                       'html_wrapper_close': '</div>',
                       'bootstrap': 'true'}
    web_response = default_web.WebResponse(response_params)
    web_response.add_head("<script src='/general_js_functions.js'></script>")

    default_web.HtmlTable.table_class_default = 'table table-striped table-bordered'

    request_path = environ['PATH_INFO'][1:]

    if request_path == '':
        web_response.add_body(default_web.main_page())

    elif request_path in db_tables:
        if environ['REQUEST_METHOD'] != 'POST':
            web_response.add_body(default_web.table_management_page(request_path))
        else:
            form_data = get_form_data(environ['wsgi.input'], int(environ['CONTENT_LENGTH']))
            web_response.add_body(default_web.table_management_page(request_path, form_data))

    elif request_path[-4:] == 'edit' and request_path[:-5] in db_tables:
        if environ['REQUEST_METHOD'] != 'POST':
            web_response.add_body(default_web.list_rows_for_editing_page(request_path[:-5]))
        else:
            form_data = get_form_data(environ['wsgi.input'], int(environ['CONTENT_LENGTH']))
            web_response.add_body(default_web.edit_db_row_page(request_path[:-5], form_data))

    elif request_path[-6:] == 'delete' and request_path[:-7] in db_tables:
        form_data = get_form_data(environ['wsgi.input'], int(environ['CONTENT_LENGTH']))
        web_response.add_body(default_web.delete_db_row_page(request_path[:-7], form_data))

    elif request_path == 'general_js_functions.js':
        with open('general_js_functions.js') as f:
            web_response.add_body(f.readlines())

        web_response.set_content_type('javascript')

    else:
        web_response.set_status('Not found')
        web_response.add_body(default_web.not_found_error_page())

    web_response.make_headers()
    start_response(web_response.status, web_response.headers)

    response = web_response.response

    return response


if check_schema():
    httpd = make_server('', 8080, application)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()