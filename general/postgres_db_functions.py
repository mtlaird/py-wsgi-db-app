import psycopg2.extras
import psycopg2.errorcodes
import json

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

class DB:
    def __init__(self):
        with open('example_db_config.json') as data_file:
            db_config = json.load(data_file, object_hook=_decode_dict)
            try:
                loaded_db_tables = db_config['db_tables']
            except KeyError:
                loaded_db_tables = False
            try:
                loaded_db_name = db_config['db_name']
            except KeyError:
                loaded_db_name = 'default'
            try:
                loaded_db_user = db_config['db_user']
            except KeyError:
                loaded_db_user = 'username'
            try:
                loaded_db_password = db_config['db_password']
            except KeyError:
                loaded_db_password = 'password'
        self.db_tables = loaded_db_tables
        self.db_name = loaded_db_name
        self.db_user = loaded_db_user
        self.db_password = loaded_db_password
        self.conn_string = "dbname = '%s' user='%s' password='%s'" % (self.db_name, self.db_user, self.db_password)
        self.db_state = 'OK'
        try:
            self.conn = psycopg2.connect(self.conn_string)
        except psycopg2.OperationalError:
            self.db_state = 'Faulted'
        if self.db_state != 'Faulted':
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def get_db_schema(self):

        res = self.run_select_command("SELECT table_name, column_name, data_type FROM information_schema.columns "
                                      "WHERE table_schema = 'public' AND table_catalog = '%s'", (self.db_name,))
        if not res:
            return False

        return res

    def run_select_command(self, command, values=None):
        if not values:
            try:
                self.cur.execute(command)
            except Exception as e:
                print e
                return False
        else:
            try:
                self.cur.execute(command, values)
            except Exception as e:
                print e
                return False

        return self.cur.fetchall()

    def run_edit_command(self, command, values):
        try:
            self.cur.execute(command, values)
        except Exception as e:
            print e
            return False

        self.conn.commit()

        return True

